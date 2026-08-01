#!/usr/bin/env python3
"""Create/update an RFPro view, run FEM, and write a compact S-parameter CSV."""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ads_profiles import profile_names, resolve_library, resolve_substrate_library, resolve_workspace
from simads.ads.rfpro import normalize_substrate_info as normalize_substrate_info_common
from simads.ads.rfpro import patch_rfpro_setup_xml
from simads.ads.workspace import find_cell_dir


def ensure_hpeesof_dir() -> None:
    if os.environ.get("HPEESOF_DIR"):
        return
    executable = Path(sys.executable).resolve()
    ads_root = executable.parents[2]
    os.environ["HPEESOF_DIR"] = str(ads_root)
    log(f"HPEESOF_DIR was not set; using {ads_root}")


def log(message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line, flush=True)
    log_path = os.environ.get("ADS_FLOW_LOG")
    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        with Path(log_path).open("a", encoding="utf-8") as fp:
            fp.write(line + "\n")


def normalize_substrate_info(
    workspace_path: str,
    library_name: str,
    cell_name: str,
    substrate_ls: tuple[str, str],
    preferred_substrate_lib: str | None = None,
) -> tuple[str, str]:
    substrate_lib, substrate_name = substrate_ls
    log(f"EM setup substrate info: {substrate_lib}:{substrate_name}")
    normalized = normalize_substrate_info_common(
        workspace_path,
        library_name,
        cell_name,
        substrate_ls,
        preferred_substrate_lib,
    )
    if normalized != substrate_ls:
        log(f"Using normalized substrate info: {normalized[0]}:{normalized[1]}")
    return normalized


def patch_existing_rfpro_setup(
    workspace_path: str,
    library_name: str,
    cell_name: str,
    rfpro_view_name: str,
    substrate_ls: tuple[str, str],
) -> None:
    cell_dir = find_cell_dir(Path(workspace_path) / library_name, cell_name)
    setup_xml = cell_dir / rfpro_view_name / "eesof_empro_setup.xml"
    if not setup_xml.exists():
        return

    log(f"Checking existing RFPro setup XML: {setup_xml}")
    changed = patch_rfpro_setup_xml(setup_xml, substrate_ls)
    if changed:
        log("Existing RFPro setup XML patched")


def ads_create_or_update_rfpro_view(
    workspace_path: str,
    library_name: str,
    cell_name: str,
    emsetup_view_name: str,
    rfpro_view_name: str,
    preferred_substrate_lib: str | None = None,
) -> dict[str, str]:
    """Runs inside an ADS Python context."""
    log("ADS RFPro prepare callable entered")
    import keysight.ads.de as de
    import keysight.ads.emtools as em

    log(f"Opening ADS workspace: {workspace_path}")
    workspace = de.open_workspace(workspace_path)
    try:
        log(f"Looking up library/cell: {library_name}:{cell_name}")
        library = de.Library.get(library_name)
        if library is None:
            raise RuntimeError(f"ADS library not found: {library_name}")
        cell = library.cell(cell_name)
        if cell is None:
            raise RuntimeError(f"ADS cell not found: {library_name}:{cell_name}")

        layout_lcv = (library_name, cell_name, "layout")
        emsetup_view = emsetup_view_name or em.find_emsetup_view_name(layout_lcv)
        emsetup_lcv = (library_name, cell_name, emsetup_view)
        substrate_ls = normalize_substrate_info(
            workspace_path,
            library_name,
            cell_name,
            em.get_substrate_info(emsetup_lcv),
            preferred_substrate_lib,
        )
        rfpro_lcv = (library_name, cell_name, rfpro_view_name)

        if not cell.view_exists(rfpro_view_name):
            log(f"Creating RFPro view: {library_name}:{cell_name}:{rfpro_view_name}")
            em.create_empro_view(rfpro_lcv, "rfpro", layout_lcv, substrate_ls)
        else:
            patch_existing_rfpro_setup(
                workspace_path,
                library_name,
                cell_name,
                rfpro_view_name,
                substrate_ls,
            )
            log(f"Updating RFPro view: {library_name}:{cell_name}:{rfpro_view_name}")
            em.update_empro_view(rfpro_lcv)
    finally:
        log(f"Closing ADS workspace: {workspace_path}")
        workspace.close()

    return {
        "workspace": workspace_path,
        "library": library_name,
        "cell": cell_name,
        "emsetup_view": emsetup_view,
        "rfpro_view": rfpro_view_name,
    }


def run_rfpro_fem(
    workspace_path: str,
    library_name: str,
    cell_name: str,
    emsetup_view_name: str,
    rfpro_view_name: str,
    analysis_name: str,
    start_freq: str,
    stop_freq: str,
    points: int,
    plan_type: str,
    max_passes: int,
    on_results_action: int | None,
    output_csv: str,
) -> dict[str, object]:
    """Runs inside an RFPro/xxPro Python context."""
    log("RFPro FEM callable entered")
    import os

    import empro
    import empro.toolkit.analysis
    import empro.toolkit.simulation
    import keysight.edatoolbox.ads as ads
    import keysight.edatoolbox.xxpro as xxpro

    os.environ["HPEESOF_DIR"] = ads.get_ads_location()
    log(f"Using ADS workspace in RFPro: {workspace_path}")
    xxpro.use_workspace(workspace_path)
    pro_lcv = ads.LibraryCellView(library=library_name, cell=cell_name, view=rfpro_view_name)
    log(f"Loading RFPro view: {library_name}:{cell_name}:{rfpro_view_name}")
    xxpro.load_pro_view(pro_lcv)

    with empro.activeProject as project:
        log(f"Creating FEM analysis from EM setup view: {emsetup_view_name}")
        analysis = empro.analysis.Analysis.fromEmSetup(emsetup_view_name)
        analysis.name = analysis_name

        options = analysis.simulationSettings
        frequency_plans = options.femFrequencyPlanList()
        frequency_plans.clear()
        plan = empro.simulation.FrequencyPlan()
        plan.type = plan_type
        plan.startFrequency = empro.core.Expression(start_freq)
        plan.stopFrequency = empro.core.Expression(stop_freq)
        plan.numberOfFrequencyPoints = points
        frequency_plans.append(plan)

        options.saveFieldsFor = "NoFrequencies"
        options.farFieldEnabled = False
        options.setPresetByName("FEM")
        if max_passes > 0:
            options.femMeshSettings.maximumNumberOfPasses = max_passes
        if on_results_action is not None:
            analysis.onResultsAction = on_results_action

        empro.activeProject.analyses.clear()
        empro.activeProject.analyses.append(analysis)
        log("Saving RFPro project before simulation")
        project.saveActiveProject()

    active_analysis = empro.activeProject.analyses[-1]
    log("Starting RFPro FEM analysis")
    empro.toolkit.analysis.runAnalysis(active_analysis, waitForConfirmation=False, saveProject=True)
    empro.activeProject.simulations.isQueueHeld = False
    active_simulation = empro.activeProject.simulations[-1]
    log("Waiting for RFPro FEM simulation")
    empro.toolkit.simulation.wait(active_simulation)
    log("RFPro FEM simulation finished; saving project")
    empro.activeProject.saveActiveProject()

    log("Exporting circuit results")
    results = empro.analysis.CircuitResults(active_analysis)
    freqs = list(results.frequencies())

    rows = []
    for idx, freq in enumerate(freqs):
        row = {"frequency_hz": float(freq)}
        for name, r, c in (("s11", 0, 0), ("s21", 1, 0), ("s12", 0, 1), ("s22", 1, 1)):
            mag = float(results.Src(r, c, "ComplexMagnitude")[idx])
            phase = float(results.Src(r, c, "Phase")[idx])
            row[f"{name}_mag"] = mag
            row[f"{name}_db"] = 20.0 * math.log10(max(mag, 1e-30))
            row[f"{name}_phase_deg"] = phase
        rows.append(row)

    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log(f"Writing RFPro CSV: {out_path}")
    with out_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return {
        "workspace": workspace_path,
        "library": library_name,
        "cell": cell_name,
        "analysis": analysis_name,
        "points": len(rows),
        "output_csv": str(out_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create/update RFPro view, run FEM, and export S-parameters.")
    parser.add_argument("--profile", default="company", choices=profile_names(), help="ADS path profile to use.")
    parser.add_argument("--workspace", type=Path, default=None, help="Override profile ADS workspace.")
    parser.add_argument("--library", default=None, help="Override profile ADS library.")
    parser.add_argument("--cell", required=True)
    parser.add_argument("--emsetup-view", default="emSetup")
    parser.add_argument("--rfpro-view", default="rfpro")
    parser.add_argument("--analysis-name", default="filter_fem")
    parser.add_argument("--start", default="4 GHz")
    parser.add_argument("--stop", default="10 GHz")
    parser.add_argument("--points", type=int, default=50)
    parser.add_argument("--plan-type", default="Adaptive", choices=["Adaptive", "Linear"])
    parser.add_argument("--max-passes", type=int, default=15)
    parser.add_argument(
        "--on-results-action",
        default=None,
        choices=["oa-emdata", "none"],
        help="Optional ADS result action; oa-emdata is the closest to the EM Setup Simulate flow.",
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument(
        "--multipython-prepare",
        action="store_true",
        help="Use multi_python.ads_context for RFPro view prepare instead of direct ADS Python APIs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log("ads_run_rfpro_fem.py started")
    workspace = resolve_workspace(args.profile, args.workspace)
    library = resolve_library(args.profile, args.library)
    substrate_library = resolve_substrate_library(args.profile, None)
    output_csv = args.out.resolve()

    ensure_hpeesof_dir()
    if args.multipython_prepare:
        log("Importing keysight.edatoolbox.multi_python")
        import keysight.edatoolbox.multi_python as multi_python

        log("Entering ADS context for RFPro view prepare")
        with multi_python.ads_context() as ads_ctx:
            log("ADS context ready; preparing RFPro view")
            prepared = ads_ctx.call(
                ads_create_or_update_rfpro_view,
                args=[str(workspace), library, args.cell, args.emsetup_view, args.rfpro_view, substrate_library],
            )
        log("ADS context closed after RFPro view prepare")
    else:
        log("Using direct ADS Python APIs for RFPro view prepare")
        prepared = ads_create_or_update_rfpro_view(
            str(workspace),
            library,
            args.cell,
            args.emsetup_view,
            args.rfpro_view,
            substrate_library,
        )
    print("RFPro view ready:", flush=True)
    for key, value in prepared.items():
        print(f"  {key}: {value}", flush=True)

    if args.prepare_only:
        log("prepare_only set; stopping before FEM")
        return

    log("Entering RFPro/xxPro context for FEM run")
    import keysight.edatoolbox.multi_python as multi_python

    with multi_python.xxpro_context() as rfpro_ctx:
        on_results_action = None
        if args.on_results_action == "oa-emdata":
            import empro

            on_results_action = empro.analysis.Analysis.OaEmdataViewORA
        result = rfpro_ctx.call(
            run_rfpro_fem,
            args=[
                str(workspace),
                library,
                args.cell,
                args.emsetup_view,
                args.rfpro_view,
                args.analysis_name,
                args.start,
                args.stop,
                args.points,
                args.plan_type,
                args.max_passes,
                on_results_action,
                str(output_csv),
            ],
        )

    log("RFPro/xxPro context closed")
    print("RFPro FEM run complete:", flush=True)
    for key, value in result.items():
        print(f"  {key}: {value}", flush=True)


if __name__ == "__main__":
    main()
