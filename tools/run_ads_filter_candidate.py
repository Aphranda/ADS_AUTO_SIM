#!/usr/bin/env python3
"""Run the ADS automation flow for one interdigital filter candidate."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from ads_profiles import get_ads_profile, profile_names, resolve_ads_python, resolve_host_python, resolve_library, resolve_workspace
from simads.config import load_project, root_relative_path
from simads.devices import get_device, list_devices
from simads.runtime import (
    artifact_entry,
    classify_exception,
    create_run_id,
    exception_summary,
    write_artifact_manifest,
    write_run_manifest,
    write_state,
)
from simads.safety import AdsWriteContext, validate_ads_cell_write

DEFAULT_TEMPLATE_CELL = "interdigital_9o_ro4350b_508um_v3_wide_mm_coords"
TARGET_SCORE_VERSIONS = {
    "ro4350_strict": "ro4350_strict_v1",
    "fr4_25db": "fr4_i7_score_v1",
    "fr4_25db_rl6": "fr4_i7_score_v1",
    "fr4_25db_rl10": "fr4_i7_score_v1",
}


def log(message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line, flush=True)
    log_path = os.environ.get("ADS_FLOW_LOG")
    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        with Path(log_path).open("a", encoding="utf-8") as fp:
            fp.write(line + "\n")


def ads_view_name(view_dir_name: str) -> str:
    return view_dir_name.replace("%", "")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_candidate_name(name: str) -> tuple[str, str]:
    cell = Path(name).stem
    base = cell.removesuffix("_mm_coords")
    return base, cell if cell.endswith("_mm_coords") else f"{cell}_mm_coords"


def default_cell_name(candidate: str) -> str:
    return normalize_candidate_name(candidate)[1]


def first_existing(paths: list[Path], description: str) -> Path:
    for path in paths:
        if path.exists():
            return path
    formatted = "\n  ".join(str(path) for path in paths)
    raise FileNotFoundError(f"{description} not found. Tried:\n  {formatted}")


def project_dirs(root: Path, project_id: str) -> dict[str, Path]:
    try:
        project = load_project(project_id, root=root)
        return {
            "layouts": project.layouts_dir,
            "results": project.results_dir,
            "runs": project.runs_dir,
        }
    except FileNotFoundError:
        pass
    project_root = root / "projects" / project_id
    return {
        "layouts": project_root / "layouts",
        "results": project_root / "results",
        "runs": project_root / "runs",
    }


def infer_round_id(*values: str) -> str:
    for value in values:
        tokens = value.replace("\\", "/").replace("_", "/").replace("-", "/").split("/")
        for token in tokens:
            lower = token.lower()
            if lower.startswith("round") and lower[5:].isdigit():
                return lower
    return "manual"


def unique_existing(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    output: list[Path] = []
    for path in paths:
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(path)
    return output


def default_candidate_files(root: Path, layouts_dir: Path, candidate: str) -> tuple[Path, Path, str]:
    base, cell = normalize_candidate_name(candidate)
    ads_dir = root / "ADS"
    dxf_candidates = unique_existing(
        [
            layouts_dir / "sweep" / f"{cell}.dxf",
            layouts_dir / f"{cell}.dxf",
            *layouts_dir.glob(f"**/{cell}.dxf"),
            ads_dir / "sweep" / f"{cell}.dxf",
            ads_dir / f"{cell}.dxf",
        ]
    )
    params_candidates = unique_existing(
        [
            layouts_dir / "sweep" / f"{base}_params.json",
            layouts_dir / f"{base}_params.json",
            *layouts_dir.glob(f"**/{base}_params.json"),
            ads_dir / "sweep" / f"{base}_params.json",
            ads_dir / f"{base}_params.json",
        ]
    )
    dxf = first_existing(
        dxf_candidates,
        "candidate DXF",
    )
    params = first_existing(
        params_candidates,
        "candidate params JSON",
    )
    return dxf, params, cell


def run_step(label: str, command: list[str], cwd: Path, dry_run: bool) -> None:
    os.environ["ADS_RUN_FAILED_STEP"] = label
    log(f"START {label}")
    print(" ".join(f'"{item}"' if " " in item else item for item in command), flush=True)
    if dry_run:
        log(f"DRY-RUN {label}")
        return
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    if "HPEESOF_DIR" not in env and command:
        exe_path = Path(command[0])
        if exe_path.name.lower() == "python.exe" and exe_path.parts[-3:-1] == ("tools", "python"):
            env["HPEESOF_DIR"] = str(exe_path.parents[2])
            log(f"Set child HPEESOF_DIR={env['HPEESOF_DIR']}")
    started = time.monotonic()
    try:
        subprocess.run(command, cwd=cwd, check=True, env=env)
    finally:
        elapsed = time.monotonic() - started
        log(f"END {label} elapsed={elapsed:.1f}s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ADS DXF import, FEM setup, RFPro FEM, and scoring.")
    parser.add_argument("candidate", help="Candidate base name, cell name, or *_mm_coords DXF stem.")
    parser.add_argument(
        "--device-id",
        default="filter.interdigital",
        choices=list_devices(),
        help="Device plugin id for manifest and compatibility checks.",
    )
    parser.add_argument("--profile", default="company", choices=profile_names(), help="ADS path profile to use.")
    parser.add_argument("--ads-python", type=Path, default=None, help="Override profile ADS Python.")
    parser.add_argument("--host-python", type=Path, default=None, help="Override profile host/control Python.")
    parser.add_argument("--workspace", type=Path, default=None, help="Override profile ADS workspace.")
    parser.add_argument("--library", default=None, help="Override profile ADS library.")
    parser.add_argument("--template-cell", default=DEFAULT_TEMPLATE_CELL, help="ADS cell to clone emSetup/em%%Setup from.")
    parser.add_argument("--setup-view", default="em%Setup", help="ADS EM setup view folder to clone.")
    parser.add_argument("--rfpro-emsetup-view", default=None, help="RFPro EM setup view name. Default derives from --setup-view.")
    parser.add_argument("--dxf", type=Path, default=None)
    parser.add_argument("--params", type=Path, default=None)
    parser.add_argument("--cell", default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--score-out", type=Path, default=None)
    parser.add_argument(
        "--score-source",
        default="rfpro-csv",
        choices=["rfpro-csv", "fem-dataset"],
        help="Score RFPro CSV or ADS workspace data/<cell>_FEM_a.ds fitted dataset.",
    )
    parser.add_argument("--project-id", default="bfp_6_8g_i7_fr4", help="Project id for run manifests.")
    parser.add_argument("--round-id", default=None, help="Round id for run manifests. Default is inferred from paths.")
    parser.add_argument("--run-id", default=None, help="Explicit run id. Default is timestamped.")
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Directory for run_manifest.json, artifact_manifest.json, and state.json.",
    )
    parser.add_argument(
        "--target-profile",
        default="ro4350_strict",
        choices=["ro4350_strict", "fr4_25db", "fr4_25db_rl6", "fr4_25db_rl10"],
    )
    parser.add_argument("--fem-dataset-suffix", default="a", help="ADS EM Setup dataset suffix after _FEM_.")
    parser.add_argument("--fem-txt-out", type=Path, default=None, help="Optional Data Display style TXT export.")
    parser.add_argument("--skip-import", action="store_true", help="Do not re-import DXF; only add/update later steps.")
    parser.add_argument("--metal-layer", default="cond", help="ADS metal layer for DXF fallback import and pins.")
    parser.add_argument("--via-layer", default="pcvia1", help="ADS via drill layer for DXF fallback import.")
    parser.add_argument("--reuse-layout", action="store_true", help="Reuse an existing layout cell and skip import/pin placement.")
    parser.add_argument("--skip-setup", action="store_true", help="Do not clone/patch the FEM setup.")
    parser.add_argument("--overwrite-setup", action="store_true", help="Overwrite target em%%Setup folder.")
    parser.add_argument("--prepare-only", action="store_true", help="Create/update RFPro view but do not start FEM.")
    parser.add_argument("--skip-fem", action="store_true", help="Stop after import/setup.")
    parser.add_argument("--skip-score", action="store_true", help="Do not run result scoring.")
    parser.add_argument("--score-only", action="store_true", help="Only score/export an existing result.")
    parser.add_argument("--force", action="store_true", help="Allow protected operations such as targeting the template cell.")
    parser.add_argument(
        "--on-results-action",
        default=None,
        choices=["oa-emdata", "none"],
        help="Optional ADS result action for the FEM run.",
    )
    parser.add_argument("--log-file", type=Path, default=None, help="Append timestamped flow logs to this file.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root()
    device_plugin = get_device(args.device_id)
    dirs = project_dirs(root, args.project_id)
    tools_dir = root / "tools"
    ads_python = resolve_ads_python(args.profile, args.ads_python)
    host_python = resolve_host_python(args.profile, args.host_python)
    workspace = resolve_workspace(args.profile, args.workspace)
    library = resolve_library(args.profile, args.library)
    rfpro_emsetup_view = args.rfpro_emsetup_view or ads_view_name(args.setup_view)

    cell = args.cell or default_cell_name(args.candidate)
    dxf = args.dxf
    params = args.params
    if (not args.score_only and not args.reuse_layout and (dxf is None or params is None)) or (not args.score_only and not args.skip_setup and params is None):
        default_dxf, default_params, default_cell = default_candidate_files(root, dirs["layouts"], args.candidate)
        dxf = dxf or default_dxf
        params = params or default_params
        cell = args.cell or default_cell

    out_csv = root_relative_path(root, args.out) if args.out else (dirs["results"] / f"{cell}_rfpro.csv")
    score_csv = (
        root_relative_path(root, args.score_out)
        if args.score_out
        else (dirs["results"] / f"{cell}_score.csv")
    )
    fem_txt_out = root_relative_path(root, args.fem_txt_out) if args.fem_txt_out else None
    fem_dataset = workspace / "data" / f"{cell}_FEM_{args.fem_dataset_suffix}.ds"
    log_file = args.log_file or (out_csv.parent / f"{cell}_flow.log")

    candidate_id, _candidate_cell = normalize_candidate_name(args.candidate)
    round_id = args.round_id or infer_round_id(str(out_csv.parent), candidate_id)
    run_id = args.run_id or create_run_id(args.project_id, round_id, candidate_id, args.profile)
    run_dir = root_relative_path(root, args.run_dir) if args.run_dir else (dirs["runs"] / run_id)
    state_path = run_dir / "state.json"
    run_manifest_path = run_dir / "run_manifest.json"
    artifact_manifest_path = run_dir / "artifact_manifest.json"
    profile = get_ads_profile(args.profile)
    score_version = TARGET_SCORE_VERSIONS[args.target_profile]
    started = time.monotonic()
    write_context = AdsWriteContext(
        profile_id=args.profile,
        workspace=workspace,
        library=library,
        template_cell=args.template_cell,
        target_cell=cell,
        force=args.force,
    )
    write_safety = write_context.to_manifest()
    if not args.score_only:
        write_safety = validate_ads_cell_write(write_context, operation="candidate_flow")

    os.environ["ADS_FLOW_LOG"] = str(log_file)
    os.environ["ADS_RUN_STATE_PATH"] = str(state_path)
    os.environ["ADS_RUN_ID"] = run_id
    os.environ["ADS_RUN_CANDIDATE_ID"] = candidate_id
    os.environ["ADS_RUN_PROFILE_ID"] = args.profile
    os.environ["ADS_RUN_FAILED_STEP"] = "planned"

    def set_state(stage: str, status: str = "running", message: str | None = None, **extra: object) -> None:
        if args.dry_run:
            return
        write_state(
            state_path,
            run_id=run_id,
            stage=stage,
            status=status,
            candidate_id=candidate_id,
            profile_id=args.profile,
            message=message,
            elapsed_s=time.monotonic() - started,
            extra=extra or None,
        )

    def write_manifests(status: str, stage: str, error_class: str | None = None) -> None:
        if args.dry_run:
            return
        write_artifact_manifest(
            artifact_manifest_path,
            run_id=run_id,
            artifacts=[
                artifact_entry("dxf", dxf, producer="generate_filter_sweep.py"),
                artifact_entry("params", params, producer="generate_filter_sweep.py"),
                artifact_entry("rfpro_csv", out_csv, producer="ads_run_rfpro_fem.py"),
                artifact_entry("fem_dataset", fem_dataset, producer="ADS RFPro/FEM"),
                artifact_entry("fem_txt", fem_txt_out, producer="export_ads_fem_dataset.py"),
                artifact_entry("score", score_csv, producer="analyze_ads_dataset.py"),
                artifact_entry("log", log_file, producer="run_ads_filter_candidate.py"),
                artifact_entry("state", state_path, producer="run_ads_filter_candidate.py"),
            ],
        )
        write_run_manifest(
            run_manifest_path,
            {
                "run_id": run_id,
                "project_id": args.project_id,
                "round_id": round_id,
                "candidate_id": candidate_id,
                "device_id": device_plugin.device_id,
                "device_plugin": {
                    "family": device_plugin.family,
                    "port_names": list(device_plugin.port_names),
                    "default_layers": device_plugin.default_layers,
                    "builder_module": device_plugin.builder_module,
                    "params_class": device_plugin.params_class,
                    "layout_builder": device_plugin.layout_builder,
                    "outputs_writer": device_plugin.outputs_writer,
                },
                "profile_id": args.profile,
                "profile_snapshot": profile.to_dict(),
                "workspace": str(workspace),
                "library": library,
                "template_cell": args.template_cell,
                "target_cell": cell,
                "setup_view": args.setup_view,
                "rfpro_emsetup_view": rfpro_emsetup_view,
                "substrate": profile.substrate,
                "target_profile_id": args.target_profile,
                "score_source": args.score_source,
                "score_version": score_version,
                "status": status,
                "stage": stage,
                "error_class": error_class,
                "state_path": str(state_path),
                "artifact_manifest_path": str(artifact_manifest_path),
                "elapsed_s": round(time.monotonic() - started, 3),
                "write_safety": write_safety,
                "flags": {
                    "dry_run": args.dry_run,
                    "skip_import": args.skip_import,
                    "reuse_layout": args.reuse_layout,
                    "skip_setup": args.skip_setup,
                    "overwrite_setup": args.overwrite_setup,
                    "prepare_only": args.prepare_only,
                    "skip_fem": args.skip_fem,
                    "skip_score": args.skip_score,
                    "score_only": args.score_only,
                    "force": args.force,
                },
            },
        )

    try:
        if not args.dry_run:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            log_file.write_text("", encoding="utf-8")
            set_state("planned", message="Candidate flow started.")
            write_manifests("running", "planned")

        log(
            "Candidate flow configured: "
            f"profile={args.profile}, workspace={workspace}, library={library}, "
            f"device_id={device_plugin.device_id}, "
            f"host_python={host_python}, ads_python={ads_python}, "
            f"cell={cell}, setup_view={args.setup_view}, rfpro_emsetup_view={rfpro_emsetup_view}, "
            f"target_profile={args.target_profile}, run_id={run_id}, run_dir={run_dir}"
        )

        if not args.dry_run and not ads_python.exists():
            raise FileNotFoundError(f"ADS Python not found: {ads_python}")

        if not args.score_only:
            if args.reuse_layout:
                os.environ["ADS_RUN_FAILED_STEP"] = "1. DXF import and P1/P2 pins"
                log("START 1. DXF import and P1/P2 pins")
                print(f"Reusing existing layout: {library}:{cell}:layout", flush=True)
                log("END 1. DXF import and P1/P2 pins")
                set_state("ads_imported", message="Existing layout reused.")
            else:
                if dxf is None or params is None:
                    raise ValueError("DXF and params are required unless --reuse-layout is used.")
                import_cmd = [
                    str(ads_python),
                    str(tools_dir / "ads_import_dxf_add_ports.py"),
                    "--profile",
                    args.profile,
                    "--workspace",
                    str(workspace),
                    "--library",
                    library,
                    "--dxf",
                    str(dxf),
                    "--params",
                    str(params),
                    "--cell",
                    cell,
                    "--metal-layer",
                    args.metal_layer,
                    "--via-layer",
                    args.via_layer,
                ]
                if args.skip_import:
                    import_cmd.append("--skip-import")
                run_step("1. DXF import and P1/P2 pins", import_cmd, root, args.dry_run)
                set_state("ads_imported")

            if not args.skip_setup:
                if params is None:
                    raise ValueError("params are required unless --skip-setup is used.")
                setup_cmd = [
                    str(host_python),
                    str(tools_dir / "ads_clone_emsetup_template.py"),
                    "--profile",
                    args.profile,
                    "--workspace",
                    str(workspace),
                    "--library",
                    library,
                    "--template-cell",
                    args.template_cell,
                    "--target-cell",
                    cell,
                    "--setup-view",
                    args.setup_view,
                    "--params",
                    str(params),
                ]
                if args.overwrite_setup:
                    setup_cmd.append("--overwrite")
                if args.force:
                    setup_cmd.append("--force")
                run_step("2. Clone/patch FEM setup", setup_cmd, root, args.dry_run)
                set_state("emsetup_ready")

            if args.skip_fem:
                log("skip_fem set; stopping after import/setup")
                set_state("emsetup_ready", status="completed", message="Stopped by --skip-fem.")
                write_manifests("completed", "emsetup_ready")
                return

            fem_cmd = [
                str(ads_python),
                str(tools_dir / "ads_run_rfpro_fem.py"),
                "--profile",
                args.profile,
                "--workspace",
                str(workspace),
                "--library",
                library,
                "--cell",
                cell,
                "--out",
                str(out_csv),
            ]
            if args.on_results_action is not None:
                fem_cmd.extend(["--on-results-action", args.on_results_action])
            fem_cmd.extend(["--emsetup-view", rfpro_emsetup_view])
            if args.prepare_only:
                fem_cmd.append("--prepare-only")
            set_state("sim_running")
            run_step("3. RFPro FEM", fem_cmd, root, args.dry_run)
            set_state("dataset_exported")

            if args.prepare_only or args.skip_score:
                set_state("emsetup_ready", status="completed", message="Stopped by --prepare-only or --skip-score.")
                write_manifests("completed", "emsetup_ready")
                return
        else:
            log("1-3. Import/setup/FEM skipped")
            print(f"Score-only mode: using existing result for {library}:{cell}", flush=True)
            set_state("dataset_exported", message="Score-only mode.")

        score_input = out_csv
        score_python = str(host_python)
        if args.score_source == "fem-dataset":
            score_input = fem_dataset
            score_python = str(ads_python)
            if not args.dry_run and not score_input.exists():
                raise FileNotFoundError(f"FEM fitted dataset not found: {score_input}")
            if fem_txt_out is not None:
                export_cmd = [
                    str(ads_python),
                    str(tools_dir / "export_ads_fem_dataset.py"),
                    "--profile",
                    args.profile,
                    "--dataset",
                    str(score_input),
                    "--out",
                    str(fem_txt_out),
                ]
                run_step("4a. Export FEM fitted dataset TXT", export_cmd, root, args.dry_run)

        score_cmd = [
            score_python,
            str(tools_dir / "analyze_ads_dataset.py"),
            str(score_input),
            "--out",
            str(score_csv),
            "--target-profile",
            args.target_profile,
            "--target-profile-id",
            args.target_profile,
            "--score-version",
            score_version,
            "--run-id",
            run_id,
            "--project-id",
            args.project_id,
            "--round-id",
            round_id,
            "--candidate-id",
            candidate_id,
            "--profile-id",
            args.profile,
            "--elapsed-s",
            f"{time.monotonic() - started:.3f}",
        ]
        run_step("4. Score S-parameters", score_cmd, root, args.dry_run)
        set_state("scored", status="completed")
        write_manifests("completed", "scored")
    except Exception as exc:
        if not args.dry_run:
            write_state(
                state_path,
                run_id=run_id,
                stage="failed",
                status="failed",
                candidate_id=candidate_id,
                profile_id=args.profile,
                failed_step=os.environ.get("ADS_RUN_FAILED_STEP"),
                error_class=classify_exception(exc),
                message=str(exc),
                elapsed_s=time.monotonic() - started,
                extra={"exception": exception_summary(exc)},
            )
            write_manifests("failed", "failed", classify_exception(exc))
        raise


if __name__ == "__main__":
    main()
