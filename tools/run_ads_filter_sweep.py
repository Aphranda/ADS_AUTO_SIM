#!/usr/bin/env python3
"""Run the generated ADS/FEM closed loop for a CSV sweep plan."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

_SIM_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _SIM_ROOT / "src"
_TOOLS_ROOT = _SIM_ROOT / "tools"
for _path in (_SRC_ROOT, _TOOLS_ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from ads_profiles import get_ads_profile, profile_names, resolve_ads_python, resolve_host_python, resolve_library, resolve_workspace
from simads.config import load_project
from simads.devices import list_devices
from simads.runtime import classify_exception, create_run_id

TARGET_SCORE_VERSIONS = {
    "ro4350_strict": "ro4350_strict_v1",
    "fr4_25db": "fr4_i7_score_v1",
    "fr4_25db_rl6": "fr4_i7_score_v1",
    "fr4_25db_rl10": "fr4_i7_score_v1",
}


def repo_root() -> Path:
    return _SIM_ROOT


def cell_name(candidate: str) -> str:
    return f"{candidate}_mm_coords" if not candidate.endswith("_mm_coords") else candidate


def infer_round_id(*values: str) -> str:
    for value in values:
        tokens = value.replace("\\", "/").replace("_", "/").replace("-", "/").split("/")
        for token in tokens:
            lower = token.lower()
            if lower.startswith("round") and lower[5:].isdigit():
                return lower
    return "manual"


def run_command(label: str, command: list[str], cwd: Path, dry_run: bool) -> float:
    print(f"\n[{label}]")
    print(" ".join(f'"{item}"' if " " in item else item for item in command))
    started = time.monotonic()
    if not dry_run:
        subprocess.run(command, cwd=cwd, check=True)
    return time.monotonic() - started


def read_plan(plan_path: Path) -> list[dict[str, str]]:
    with plan_path.open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fp:
        data = json.load(fp)
    return data if isinstance(data, dict) else {}


def run_context(run_dir: Path) -> dict[str, str]:
    state = read_json(run_dir / "state.json")
    manifest = read_json(run_dir / "run_manifest.json")
    context: dict[str, str] = {}
    for key in ("run_id", "project_id", "round_id", "candidate_id", "profile_id", "target_profile_id", "score_version"):
        value = manifest.get(key)
        if value is not None:
            context[key] = str(value)
    for key in ("run_id", "candidate_id", "profile_id", "status", "failed_step", "error_class", "elapsed_s"):
        value = state.get(key)
        if value is not None:
            context[key] = str(value)
    return context


def ordered_fieldnames(rows: list[dict[str, str]]) -> list[str]:
    preferred = [
        "candidate",
        "cell",
        "status",
        "error_class",
        "failed_step",
        "elapsed_s",
        "run_id",
        "profile_id",
        "target_profile_id",
        "score_version",
        "notes",
    ]
    seen: set[str] = set()
    fields: list[str] = []
    for key in preferred:
        if any(key in row for row in rows):
            fields.append(key)
            seen.add(key)
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)
    return fields


def write_summary(
    run_infos: list[dict[str, object]],
    plan_rows: dict[str, dict[str, str]],
    out_path: Path,
    failed_rows: list[dict[str, str]] | None = None,
    *,
    profile_id: str,
    target_profile_id: str,
) -> None:
    rows: list[dict[str, str]] = []
    for info in run_infos:
        score_path = Path(str(info["score_path"]))
        run_dir = Path(str(info["run_dir"]))
        context = run_context(run_dir)
        if not score_path.exists():
            continue
        with score_path.open(newline="", encoding="utf-8") as fp:
            for row in csv.DictReader(fp):
                source = Path(row["source"])
                candidate_cell = source.stem.removesuffix("_rfpro")
                candidate = (
                    context.get("candidate_id")
                    or row.get("candidate_id")
                    or str(info.get("candidate", ""))
                    or candidate_cell.removesuffix("_mm_coords")
                )
                plan = plan_rows.get(candidate, {})
                state_status = context.get("status", "")
                score_status = row.get("status", "scored")
                status = state_status if state_status == "failed" else score_status
                rows.append(
                    {
                        **row,
                        "candidate": candidate,
                        "cell": candidate_cell,
                        "status": status,
                        "error_class": context.get("error_class", row.get("error_class", "")),
                        "failed_step": context.get("failed_step", row.get("failed_step", "")),
                        "elapsed_s": context.get("elapsed_s", row.get("elapsed_s", "")),
                        "run_id": context.get("run_id", row.get("run_id", str(info.get("run_id", "")))),
                        "run_dir": str(run_dir),
                        "profile_id": context.get("profile_id", row.get("profile_id", profile_id)),
                        "target_profile_id": context.get("target_profile_id", row.get("target_profile_id", target_profile_id)),
                        "score_version": context.get("score_version", row.get("score_version", "")),
                        "notes": plan.get("notes", ""),
                    }
                )

    rows.extend(failed_rows or [])
    if not rows:
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ordered_fieldnames(rows)
    with out_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote sweep summary: {out_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate, simulate, score, and summarize ADS filter candidates.")
    parser.add_argument("--plan", type=Path, default=None, help="Sweep plan CSV. Default uses the active project sweep.")
    parser.add_argument("--out-dir", type=Path, default=None, help="Generated layout directory. Default uses the active project sweep.")
    parser.add_argument("--results-dir", type=Path, default=None, help="Result directory. Default uses the active project sweep.")
    parser.add_argument("--summary", type=Path, default=None, help="Sweep summary CSV. Default uses the active project sweep.")
    parser.add_argument("--profile", default="company", choices=profile_names(), help="ADS path profile to use.")
    parser.add_argument("--ads-python", type=Path, default=None, help="Override profile ADS Python.")
    parser.add_argument("--host-python", type=Path, default=None, help="Override profile host/control Python.")
    parser.add_argument("--workspace", type=Path, default=None, help="Override profile ADS workspace.")
    parser.add_argument("--library", default=None, help="Override profile ADS library.")
    parser.add_argument("--project-id", default="bfp_6_8g_i7_fr4", help="Project id passed to run manifests.")
    parser.add_argument("--sweep-id", default=None, help="Optional sweep id from project config.")
    parser.add_argument(
        "--device-id",
        default=None,
        choices=list_devices(),
        help="Device plugin id passed to candidate manifests. Default uses the project config primary_device_type.",
    )
    parser.add_argument("--round-id", default=None, help="Round id passed to run manifests. Default is inferred from paths.")
    parser.add_argument(
        "--template-cell",
        default=None,
        help="ADS cell to clone the EM setup from. Default uses the active project sweep, then the profile.",
    )
    parser.add_argument("--setup-view", default=None, help="ADS EM setup view folder to clone. Default uses the active project sweep.")
    parser.add_argument(
        "--rfpro-emsetup-view",
        default=None,
        help="RFPro EM setup view name. Default derives from --setup-view in the candidate runner.",
    )
    parser.add_argument(
        "--target-profile",
        default=None,
        choices=["ro4350_strict", "fr4_25db", "fr4_25db_rl6", "fr4_25db_rl10"],
        help="Scoring target profile. Default uses the active project sweep.",
    )
    parser.add_argument("--candidates", nargs="*", default=None, help="Optional candidate names to run.")
    parser.add_argument("--skip-generate", action="store_true")
    parser.add_argument("--force-import-existing", action="store_true", help="Attempt to import even if the ADS cell exists.")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-fem", action="store_true")
    parser.add_argument(
        "--score-source",
        default="rfpro-csv",
        choices=["rfpro-csv", "fem-dataset"],
        help="Score RFPro CSV or ADS workspace data/<cell>_FEM_a.ds fitted dataset.",
    )
    parser.add_argument("--fem-dataset-suffix", default="a")
    parser.add_argument("--export-fem-txt", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def default_project_paths(root: Path, project_id: str) -> tuple[Path, Path, Path, Path]:
    project = root / "projects" / project_id
    plan = project / "plans" / "filter_opt_i7_fr4_round7.csv"
    layouts = project / "layouts" / "interdigital_7o_fr4_210um_round7"
    results = project / "results" / "interdigital_7o_fr4_210um_round7"
    summary = results / "sweep_summary.csv"
    return plan, layouts, results, summary


def apply_project_defaults(args: argparse.Namespace, root: Path) -> None:
    try:
        project = load_project(args.project_id, root=root)
    except FileNotFoundError:
        project = None
    sweep = project.get_sweep(args.sweep_id) if project else None
    fallback_plan, fallback_layouts, fallback_results, fallback_summary = default_project_paths(root, args.project_id)
    profile = resolve_profile(args.profile, sweep.profile if sweep else None)

    args._project_config = project
    args._sweep_config = sweep
    args.profile = profile
    args.plan = args.plan or (sweep.plan if sweep else None) or fallback_plan
    args.out_dir = args.out_dir or (sweep.layouts_dir if sweep else None) or fallback_layouts
    args.results_dir = args.results_dir or (sweep.results_dir if sweep else None) or fallback_results
    args.summary = args.summary or (sweep.summary if sweep else None) or fallback_summary
    args.device_id = (
        args.device_id
        or (sweep.device_id if sweep else None)
        or (project.primary_device_type if project else None)
        or "filter.interdigital"
    )
    args.target_profile = args.target_profile or (sweep.target_profile if sweep else None) or (project.target_profile if project else None) or "ro4350_strict"
    ads_profile = get_ads_profile(args.profile)
    args.template_cell = (
        args.template_cell
        or (sweep.template_cell if sweep else None)
        or ads_profile.template_cell
        or (project.ads.template_cell if project and project.ads.template_cell else None)
        or "interdigital_9o_ro4350b_508um_v3_wide_mm_coords"
    )
    args.setup_view = args.setup_view or (sweep.setup_view if sweep else None) or ads_profile.setup_view or (project.ads.setup_view if project else None) or "em%Setup"
    args.rfpro_emsetup_view = args.rfpro_emsetup_view or (sweep.rfpro_emsetup_view if sweep else None) or ads_profile.rfpro_emsetup_view


def resolve_profile(current: str, configured: str | None) -> str:
    return current or configured or "company"


def main() -> None:
    args = parse_args()
    root = repo_root()
    tools_dir = root / "tools"
    apply_project_defaults(args, root)
    device_id = args.device_id
    ads_python = resolve_ads_python(args.profile, args.ads_python)
    host_python = resolve_host_python(args.profile, args.host_python)
    workspace = resolve_workspace(args.profile, args.workspace)
    library = resolve_library(args.profile, args.library)
    rows = read_plan(args.plan)
    selected = args.candidates or [row["name"].strip() for row in rows]
    plan_rows = {row["name"].strip(): row for row in rows}
    round_id = args.round_id or infer_round_id(str(args.plan), str(args.out_dir), str(args.results_dir), str(args.summary))
    score_version = TARGET_SCORE_VERSIONS[args.target_profile]

    if not args.skip_generate:
        run_command(
            "Generate candidate DXF/JSON files",
            [
                str(host_python),
                str(tools_dir / "generate_filter_sweep.py"),
                "--plan",
                str(args.plan),
                "--out-dir",
                str(args.out_dir),
            ],
            root,
            args.dry_run,
        )

    run_infos: list[dict[str, object]] = []
    failed_rows: list[dict[str, str]] = []
    for candidate in selected:
        cell = cell_name(candidate)
        run_id = create_run_id(args.project_id, round_id, candidate, args.profile)
        run_dir = args.results_dir / "runs" / run_id
        score_path = args.results_dir / f"{cell}_score.csv"
        run_infos.append({"candidate": candidate, "cell": cell, "run_id": run_id, "run_dir": run_dir, "score_path": score_path})
        existing_layout = workspace / library / cell / "layout"
        command = [
            str(host_python),
            str(tools_dir / "run_ads_filter_candidate.py"),
            candidate,
            "--device-id",
            device_id,
            "--profile",
            args.profile,
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
            round_id,
            "--run-id",
            run_id,
            "--run-dir",
            str(run_dir),
            "--template-cell",
            args.template_cell,
            "--setup-view",
            args.setup_view,
            "--dxf",
            str(args.out_dir / f"{cell}.dxf"),
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
        if args.export_fem_txt:
            command.extend(["--fem-txt-out", str(args.results_dir / f"{cell}_FEM_{args.fem_dataset_suffix}.txt")])
        if existing_layout.exists() and not args.force_import_existing:
            command.append("--reuse-layout")
        if args.prepare_only:
            command.append("--prepare-only")
        if args.skip_fem:
            command.append("--skip-fem")

        started = time.monotonic()
        try:
            run_command(f"Run ADS/FEM candidate {candidate}", command, root, args.dry_run)
        except subprocess.CalledProcessError as exc:
            elapsed = time.monotonic() - started
            failed_rows.append(
                {
                    "candidate": candidate,
                    "cell": cell,
                    "status": "failed",
                    "error_class": classify_exception(exc),
                    "failed_step": "run_ads_filter_candidate.py",
                    "elapsed_s": f"{elapsed:.1f}",
                    "run_id": run_id,
                    "run_dir": str(run_dir),
                    "profile_id": args.profile,
                    "target_profile_id": args.target_profile,
                    "score_version": score_version,
                    "notes": plan_rows.get(candidate, {}).get("notes", ""),
                }
            )
            if not args.continue_on_error:
                raise
            print(f"Candidate failed, continuing: {candidate}")

    if not args.prepare_only and not args.skip_fem and not args.dry_run:
        write_summary(run_infos, plan_rows, args.summary, failed_rows, profile_id=args.profile, target_profile_id=args.target_profile)


if __name__ == "__main__":
    main()
