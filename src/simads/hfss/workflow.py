#!/usr/bin/env python3
"""Run an HFSS 3D Layout verdict simulation from a SIM layout JSON."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from simads.config import StackupConfig, get_hfss_profile, hfss_profile_names, load_stackup_config
from simads.domain import SimulationResultSpec, StackupSpec, SweepSpec
from simads.runtime import (
    SimulationManifestPayload,
    SimulationRunContext,
    artifact_entry,
    build_simulation_artifacts,
    classify_exception,
    exception_summary,
    write_simulation_manifests,
)
from simads.hfss.artifacts import (
    HFSS_PROJECT_ACTION_ADD,
    HFSS_PROJECT_ACTION_NEW,
    HFSS_PROJECT_ACTIONS,
    HFSS_PROJECT_MODEL_PER_DESIGN,
    HFSS_PROJECT_MODELS,
    default_project_name,
    expected_hfss_outputs,
    resolve_project_path,
)
from simads.hfss.build import build_hfss_layout_project
from simads.hfss.connector import FIXTURE_TYPE as MICROSTRIP_CONNECTOR_FIXTURE_TYPE
from simads.hfss.connector import SINGLE_CONNECTOR_FIXTURE_TYPE
from simads.hfss.layout_io import collect_layout_summary, configured_layout_id, load_layout
from simads.hfss.plans import RELIABLE_HFSS_ROUTE, apply_hfss_route_defaults
from simads.hfss.ports import (
    BOTTOM_LAYER,
    TOP_LAYER,
    create_gap_edge_ports_in_edb,
    infer_pin_ports,
    patch_gap_ports_in_edb,
    port_reference_name,
    project_edb_path,
    resolve_gnd_boundary,
    resolve_port_edges,
)
from simads.hfss.solve import solve_and_export_hfss
from simads.hfss.stackup import (
    DIELECTRIC_LAYER,
    FR4_MATERIAL,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
AEDT_VERSION = "2026.1"


def stackup_config_from_args(args: argparse.Namespace) -> StackupConfig | None:
    existing = getattr(args, "_stackup_config", None)
    if existing is not None:
        return existing
    stackup_config_path = getattr(args, "stackup_config", None)
    if stackup_config_path is None:
        return None
    config = load_stackup_config(stackup_config_path)
    args._stackup_config = config
    args.signal_layer = config.geometry.signal_layer
    args.reference_ground_layer = config.geometry.reference_ground_layer
    args.via_top_layer = config.geometry.via_top_layer
    args.via_bottom_layer = config.geometry.via_bottom_layer
    args.ground_plane_name = config.geometry.ground_plane_name
    return config


def _layer_thickness(stackup: StackupConfig, layer_name: str) -> float:
    for layer in stackup.layers_bottom_to_top:
        if layer.name == layer_name:
            return layer.thickness_mm
    raise ValueError(f"stackup layer not found: {layer_name}")


def _manifest_stackup(args: argparse.Namespace, metadata: dict[str, Any]) -> StackupSpec:
    config = stackup_config_from_args(args)
    if config is not None:
        primary = config.primary_dielectric
        er = float(args.er if args.er is not None else (primary.er if primary and primary.er is not None else 4.6))
        loss_tangent = float(
            args.loss_tangent
            if args.loss_tangent is not None
            else (primary.loss_tangent if primary and primary.loss_tangent is not None else 0.02)
        )
        return StackupSpec(
            stackup_id=str(args.stackup_id or config.stackup_id),
            dielectric_material=primary.name if primary is not None else "unknown_dielectric",
            er=er,
            loss_tangent=loss_tangent,
            dielectric_height_mm=config.signal_to_reference_height_mm,
            copper_thickness_mm=_layer_thickness(config, config.geometry.signal_layer),
            top_layer=config.geometry.signal_layer,
            dielectric_layer="configured_multilayer",
            bottom_layer=config.geometry.reference_ground_layer,
            config_path=str(getattr(args, "stackup_config", "")),
            signal_to_reference_height_mm=config.signal_to_reference_height_mm,
            total_thickness_mm=config.total_thickness_mm,
            layers_bottom_to_top=[layer.to_dict() for layer in config.layers_bottom_to_top],
            geometry=config.geometry.to_dict(),
        )
    stackup_id = str(args.stackup_id or metadata.get("substrate") or "unknown_stackup")
    return StackupSpec(
        stackup_id=stackup_id,
        dielectric_material=FR4_MATERIAL,
        er=float(args.er if args.er is not None else metadata.get("er", 4.6)),
        loss_tangent=float(args.loss_tangent if args.loss_tangent is not None else 0.02),
        dielectric_height_mm=float(args.substrate_height_mm or metadata.get("dielectric_height_mm", 0.21)),
        copper_thickness_mm=float(args.copper_thickness_mm or metadata.get("copper_thickness_mm", 0.035)),
        top_layer=TOP_LAYER,
        dielectric_layer=DIELECTRIC_LAYER,
        bottom_layer=BOTTOM_LAYER,
    )


def infer_round_id(*values: str | Path | None) -> str:
    for value in values:
        if value is None:
            continue
        tokens = str(value).replace("\\", "/").replace("_", "/").replace("-", "/").split("/")
        for token in tokens:
            lower = token.lower()
            if lower.startswith("round") and lower[5:].isdigit():
                return lower
    return "manual"


def default_candidate_id(layout: dict[str, Any], args: argparse.Namespace) -> str:
    return str(args.candidate_id or configured_layout_id(layout) or args.project_name or "hfss_verdict")


def _connector_params_json(args: argparse.Namespace, metadata: dict[str, Any]) -> Path | None:
    explicit = getattr(args, "connector_params_json", None)
    if explicit is not None:
        return explicit
    metadata_path = metadata.get("connector_params_json")
    if metadata_path:
        return Path(str(metadata_path))
    layout_path = getattr(args, "layout", None)
    if layout_path is None:
        return None
    layout_path = Path(layout_path)
    name = layout_path.name
    if name.endswith("_layout.json"):
        inferred = layout_path.with_name(f"{name.removesuffix('_layout.json')}_params.json")
        if inferred.exists():
            return inferred
    return None


def _connector_port_reference_name(args: argparse.Namespace, metadata: dict[str, Any]) -> str:
    explicit = getattr(args, "port_reference_name", None)
    if explicit:
        return str(explicit)
    layer = metadata.get("reference_ground_layer") or getattr(args, "reference_ground_layer", None)
    primitive = metadata.get("ground_plane_name") or getattr(args, "ground_plane_name", None)
    if layer or primitive:
        return f"GND:{layer or BOTTOM_LAYER}:{primitive or 'hfss_ground_plane'}"
    return port_reference_name(args)


def connector_fixture_metadata(args: argparse.Namespace, layout: dict[str, Any]) -> dict[str, Any]:
    metadata = layout.get("metadata", {})
    fixture_type = metadata.get("fixture_type")
    if fixture_type not in {MICROSTRIP_CONNECTOR_FIXTURE_TYPE, SINGLE_CONNECTOR_FIXTURE_TYPE}:
        return {}
    params_json = _connector_params_json(args, metadata)
    model_path = getattr(args, "connector_hfss_model_path", None) or metadata.get("connector_hfss_model_path")
    model_version = getattr(args, "connector_hfss_model_version", None) or metadata.get("connector_hfss_model_version")
    model_hash = getattr(args, "connector_hfss_model_hash", None) or metadata.get("connector_hfss_model_hash")
    port_mapping = getattr(args, "connector_port_mapping", None) or metadata.get("connector_port_mapping")
    stackup_config = getattr(args, "stackup_config", None) or metadata.get("stackup_config")
    port_deembed_mm = float(metadata.get("port_deembed_mm", 0.0) or 0.0)
    reference_plane_offset_mm = float(metadata.get("reference_plane_offset_mm", 0.0) or 0.0)
    return {
        "fixture_type": fixture_type,
        "connector_model_version": metadata.get("connector_model_version"),
        "connector_route": metadata.get("connector_route"),
        "connector_type": metadata.get("connector_type"),
        "microstrip_connector_layout_json": str(getattr(args, "layout", "")),
        "connector_params_json": str(params_json) if params_json is not None else None,
        "line_w_mm": metadata.get("line_w_mm"),
        "line_l_mm": metadata.get("line_l_mm"),
        "reference_plane_offset_mm": reference_plane_offset_mm,
        "port_deembed_mm": port_deembed_mm,
        "connector_region_bbox_mm": metadata.get("connector_region_bbox_mm"),
        "connector_port_contract": {
            "route": str(getattr(args, "route", "custom") or "custom"),
            "port_type": getattr(args, "port_type", None),
            "gnd_boundary_mode": getattr(args, "gnd_boundary_mode", None),
            "reference_ground_ports": bool(getattr(args, "reference_ground_ports", False)),
            "reference_name": _connector_port_reference_name(args, metadata),
            "renormalize": True,
            "renormalize_impedance_ohm": 50.0,
            "reference_plane_offset_mm": reference_plane_offset_mm,
            "port_deembed_mm": port_deembed_mm,
            "deembed_enabled": port_deembed_mm > 0.0,
        },
        "stackup_config": str(stackup_config) if stackup_config is not None else None,
        "connector_hfss_model_path": str(model_path) if model_path is not None else None,
        "connector_hfss_model_version": model_version,
        "connector_hfss_model_hash": model_hash,
        "connector_port_mapping": port_mapping,
    }


def hfss_dry_run_payload(
    args: argparse.Namespace,
    layout: dict[str, Any],
    *,
    summary: dict[str, Any],
    stackup_config: StackupConfig | None,
    manifest_context: SimulationRunContext,
    run_id: str,
    run_dir: Path,
) -> dict[str, Any]:
    port_edges = resolve_port_edges(layout, args.p1_edge, args.p2_edge, args.p1_ref_edge, args.p2_ref_edge)
    pin_ports = infer_pin_ports(layout)
    connector = connector_fixture_metadata(args, layout)
    payload: dict[str, Any] = {
        "mode": "dry_run",
        "summary": summary,
        "port_type": args.port_type,
        "route": args.route,
        "gnd_boundary": resolve_gnd_boundary(layout, args),
        "reference_ground_ports": args.reference_ground_ports,
        "port_edges": port_edges,
        "pin_ports": pin_ports,
        "gap_port_template": {
            "reference_name": port_reference_name(args),
            "resolved_reference_name": port_reference_name(args),
            "pec_launch_width": args.port_pec_launch_width,
            "horizontal_extent_factor": args.port_horizontal_extent_factor,
            "vertical_extent_factor": args.port_vertical_extent_factor,
            "radial_extent_factor": args.port_radial_extent_factor,
            "type": "Single Strip Gap Source",
            "hfss_type": "Gap",
        },
        "stackup_config": stackup_config.to_dict() if stackup_config is not None else None,
        "extents": {
            "configure": args.configure_extents,
            "diel_extent_type": args.diel_extent_type,
            "diel_horizontal_padding": args.diel_horizontal_padding,
            "diel_honor_primitives": args.diel_honor_primitives,
            "include_3d_subdesigns": args.include_3d_subdesigns,
            "airbox_extent_type": args.airbox_extent_type,
            "truncate_airbox_at_ground": args.truncate_airbox_at_ground,
            "airbox_horizontal_padding": args.airbox_horizontal_padding,
            "airbox_vertical_positive_padding": args.airbox_vertical_positive_padding,
            "airbox_vertical_negative_padding": args.airbox_vertical_negative_padding,
            "airbox_vertical_sync": args.airbox_vertical_sync,
            "open_region_type": args.open_region_type,
            "use_radiation_boundary": args.use_radiation_boundary,
            "open_region_frequency_ghz": args.open_region_frequency_ghz,
            "radiation_factor": args.radiation_factor,
        },
        "design_options": {
            "enable_design_intersection_check": args.enable_design_intersection_check,
        },
        "manifest": {
            "write_manifest": args.write_manifest,
            "run_id": run_id,
            "run_dir": str(run_dir),
            "project_id": args.project_id,
            "round_id": manifest_context.round_id,
            "candidate_id": manifest_context.candidate_id,
            "profile_id": args.profile_id,
        },
        "project_contract": {
            "project_model": args.project_model,
            "project_action": args.project_action,
            "reuse_project": args.reuse_project,
            "project": str(resolve_project_path(args, layout)),
            "design": args.design,
        },
    }
    if connector:
        payload["connector"] = connector
    return payload


def build_hfss_manifest_payload(
    args: argparse.Namespace,
    layout: dict[str, Any],
    *,
    run_id: str,
    result: dict[str, Any] | None = None,
    error: BaseException | None = None,
) -> SimulationManifestPayload:
    metadata = layout.get("metadata", {})
    route = str(getattr(args, "route", "custom") or "custom")
    round_id = args.round_id or infer_round_id(args.layout, args.out_dir, args.project_name)
    outputs = expected_hfss_outputs(args, layout)
    stackup = _manifest_stackup(args, metadata)
    connector = connector_fixture_metadata(args, layout)
    inputs = {"layout_json": str(args.layout)}
    if connector:
        inputs["microstrip_connector_layout_json"] = connector["microstrip_connector_layout_json"]
        inputs["connector_params_json"] = connector["connector_params_json"]
        inputs["connector_hfss_model_path"] = connector["connector_hfss_model_path"]
    sweep = SweepSpec(
        start_ghz=float(args.start_ghz),
        stop_ghz=float(args.stop_ghz),
        points=int(args.points),
        sweep_type=args.sweep_type,
        adaptive_frequency_ghz=float(args.adaptive_frequency_ghz),
    )
    result_spec = SimulationResultSpec(
        simulator="hfss3dlayout",
        project=(result or {}).get("project") or outputs["project"],
        design=args.design,
        s2p=(result or {}).get("s2p") or outputs["s2p"],
        trace_csv=(result or {}).get("trace_csv") or outputs["trace_csv"],
        score_csv=(result or {}).get("score") or outputs["score_csv"],
        svg=outputs["svg"],
        summary_csv=outputs["summary_csv"],
    )
    return SimulationManifestPayload(
        context=SimulationRunContext(
            project_id=args.project_id,
            round_id=round_id,
            candidate_id=default_candidate_id(layout, args),
            profile_id=args.profile_id,
            simulator="hfss3dlayout",
            run_id=run_id,
            run_dir=args.run_dir,
            device_id=args.device_id,
            pipeline_id=getattr(args, "pipeline_id", None),
            profile_snapshot={
                "hfss_version": args.version,
                "workspace_dir": str(args.workspace_dir),
                "project_model": args.project_model,
                "project_action": args.project_action,
                "design": args.design,
                "setup": args.setup,
                "sweep": args.sweep,
                "route": route,
            },
        ),
        sweep=sweep,
        stackup=stackup,
        inputs=inputs,
        outputs={
            "aedt_project": str(outputs["project"]),
            "s2p": str(outputs["s2p"]),
            "score_csv": str(outputs["score_csv"]),
            "trace_csv": str(outputs["trace_csv"]),
            "summary_csv": str(outputs["summary_csv"]),
            "svg": str(outputs["svg"]),
        },
        flags={
            "dry_run": args.dry_run,
            "build_only": args.build_only,
            "project_model": args.project_model,
            "project_action": args.project_action,
            "reuse_project": args.reuse_project,
            "skip_ports": args.skip_ports,
            "skip_port_number": list(getattr(args, "skip_port_number", [])),
            "non_graphical": args.non_graphical,
            "keep_open": args.keep_open,
            "configure_extents": args.configure_extents,
            "route": route,
            "gnd_boundary_mode": args.gnd_boundary_mode,
            "port_type": args.port_type,
            "reference_ground_ports": args.reference_ground_ports,
            "stackup_config": str(getattr(args, "stackup_config", "")) if getattr(args, "stackup_config", None) is not None else None,
            "enable_design_intersection_check": args.enable_design_intersection_check,
            "fixture_type": connector.get("fixture_type") if connector else metadata.get("fixture_type"),
        },
        result=result_spec,
        extra={
            **connector,
            "layout_summary": collect_layout_summary(layout),
            "port_edges": resolve_port_edges(layout, args.p1_edge, args.p2_edge, args.p1_ref_edge, args.p2_ref_edge),
            "gnd_boundary": resolve_gnd_boundary(layout, args),
            "error": exception_summary(error) if error is not None else None,
        },
    )


def write_hfss_manifests(
    args: argparse.Namespace,
    layout: dict[str, Any],
    *,
    run_id: str,
    run_dir: Path,
    status: str,
    stage: str,
    elapsed_s: float,
    result: dict[str, Any] | None = None,
    error: BaseException | None = None,
) -> dict[str, Path]:
    outputs = expected_hfss_outputs(args, layout)
    payload = build_hfss_manifest_payload(args, layout, run_id=run_id, result=result, error=error)
    connector_artifacts = None
    if layout.get("metadata", {}).get("fixture_type") in {MICROSTRIP_CONNECTOR_FIXTURE_TYPE, SINGLE_CONNECTOR_FIXTURE_TYPE}:
        connector_artifacts = [
            artifact_entry("microstrip_connector_layout_json", args.layout, producer="run_hfss3dlayout_filter_verdict.py"),
            artifact_entry(
                "connector_params",
                Path(payload.inputs["connector_params_json"]) if payload.inputs.get("connector_params_json") else None,
                producer="run_hfss3dlayout_filter_verdict.py",
            ),
            artifact_entry(
                "connector_hfss_model",
                Path(payload.inputs["connector_hfss_model_path"]) if payload.inputs.get("connector_hfss_model_path") else None,
                producer="run_hfss3dlayout_filter_verdict.py",
            ),
        ]
    artifacts = build_simulation_artifacts(
        layout_json=args.layout,
        project_file=Path((result or {}).get("project") or outputs["project"]),
        s2p=Path((result or {}).get("s2p") or outputs["s2p"]),
        trace_csv=Path((result or {}).get("trace_csv") or outputs["trace_csv"]),
        score_csv=Path((result or {}).get("score") or outputs["score_csv"]),
        svg=outputs["svg"],
        summary_csv=outputs["summary_csv"],
        state=run_dir / "state.json",
        producer="run_hfss3dlayout_filter_verdict.py",
        extra=connector_artifacts,
    )
    return write_simulation_manifests(
        run_dir=run_dir,
        run_id=run_id,
        payload=payload,
        artifacts=artifacts,
        status=status,
        stage=stage,
        error_class=classify_exception(error) if error is not None else None,
        elapsed_s=elapsed_s,
        message=str(error) if error is not None else f"HFSS workflow {status}.",
    )


def completed_hfss_stage(args: argparse.Namespace, result: dict[str, Any]) -> str:
    if getattr(args, "build_only", False):
        return "setup_ready"
    if result.get("post_processed"):
        return "scored"
    if result.get("s2p"):
        return "results_exported"
    return "completed"


def run_hfss(args: argparse.Namespace) -> dict[str, Any]:
    from ansys.aedt.core import Hfss3dLayout

    apply_hfss_route_defaults(args)
    layout = load_layout(args.layout)
    stackup_config = stackup_config_from_args(args)
    project = resolve_project_path(args, layout)
    if args.project_action == HFSS_PROJECT_ACTION_ADD and args.project is None and args.project_name is None:
        raise ValueError("--project-action add requires --project or --project-name to identify the project space")
    project.parent.mkdir(parents=True, exist_ok=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    reuse_project = args.reuse_project or args.project_action == HFSS_PROJECT_ACTION_ADD
    init_project = str(project) if reuse_project and project.exists() else None

    app = Hfss3dLayout(
        project=init_project,
        design=args.design,
        version=args.version,
        non_graphical=args.non_graphical,
        new_desktop=True,
        close_on_exit=not args.keep_open,
        remove_lock=True,
    )
    desktop_released = False
    try:
        result = build_hfss_layout_project(
            app,
            layout,
            args,
            project_path=project,
            stackup_config=stackup_config,
        ).to_dict()
        result["layout"] = str(args.layout)
        if args.patch_edb_port_properties and args.port_type in {"edge-gap", "pin-gap"} and not args.skip_ports:
            if args.keep_open:
                result["edb_port_patch"] = {"skipped": True, "reason": "keep_open"}
            else:
                app.release_desktop(close_projects=True, close_desktop=True)
                desktop_released = True
                if args.port_type == "edge-gap":
                    result["edb_port_patch"] = create_gap_edge_ports_in_edb(project_edb_path(project), layout, args)
                    result["ports"] = ["Port1", "Port2"]
                    result["saved_after_edb_patch"] = False
                    continue_after_patch = not args.build_only
                    if args.build_only:
                        result["post_patch_reopen_skipped"] = "preserve_pyedb_edge_ports"
                else:
                    result["edb_port_patch"] = patch_gap_ports_in_edb(project_edb_path(project), args)
                    continue_after_patch = True
                if continue_after_patch:
                    app = Hfss3dLayout(
                        project=str(project),
                        design=args.design,
                        version=args.version,
                        non_graphical=args.non_graphical,
                        new_desktop=True,
                        close_on_exit=True,
                        remove_lock=True,
                    )
                    desktop_released = False
                    app.modeler.model_units = "mm"
                    if args.port_type == "edge-gap":
                        result["post_patch_reopened_for_solve"] = True
                    else:
                        result["saved_after_edb_patch"] = bool(app.save_project(str(project), overwrite=True))
        if not args.build_only:
            result.update(solve_and_export_hfss(app, layout, args).to_dict())
        return result
    finally:
        if not args.keep_open and not desktop_released:
            app.release_desktop(close_projects=True, close_desktop=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build/run an HFSS 3D Layout verdict case from SIM layout JSON.")
    parser.add_argument("--profile", default="auto", choices=hfss_profile_names(include_auto=True), help="HFSS/AEDT path profile to use.")
    parser.add_argument("--layout", type=Path, required=True, help="SIM *_layout.json file.")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--workspace-dir", type=Path, default=None)
    parser.add_argument("--project", type=Path, default=None)
    parser.add_argument("--project-name", default=None)
    parser.add_argument(
        "--project-model",
        choices=HFSS_PROJECT_MODELS,
        default=HFSS_PROJECT_MODEL_PER_DESIGN,
        help=(
            "HFSS AEDT organization model. per_design_project keeps the historical one-project-per-case flow; "
            "single_aedt_project_multiple_designs stores multiple designs in one AEDT project."
        ),
    )
    parser.add_argument(
        "--project-action",
        choices=HFSS_PROJECT_ACTIONS,
        default=HFSS_PROJECT_ACTION_NEW,
        help="new creates a fresh project path; add opens the named project and appends the requested design.",
    )
    parser.add_argument("--reuse-project", action="store_true")
    parser.add_argument("--design", default="I7_FR4_HFSS_VERDICT")
    parser.add_argument("--version", default=None)
    parser.add_argument("--non-graphical", action="store_true")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--route",
        choices=["custom", "reliable", RELIABLE_HFSS_ROUTE],
        default=None,
        help="HFSS route preset. reliable expands to AEDT edge gap ports with port-edge GND.",
    )
    parser.add_argument("--substrate-height-mm", type=float, default=None)
    parser.add_argument("--copper-thickness-mm", type=float, default=None)
    parser.add_argument("--stackup-config", type=Path, default=None, help="PCB stackup JSON config. Overrides the legacy 2-layer stackup model.")
    parser.add_argument("--er", type=float, default=None)
    parser.add_argument("--loss-tangent", type=float, default=None)
    parser.add_argument(
        "--gnd-boundary-mode",
        choices=["em-boundary", "port-edges"],
        default="em-boundary",
        help="HFSS GND plane extent. port-edges aligns left/right GND edges to P1/P2 port cross sections.",
    )
    parser.add_argument("--start-ghz", type=float, default=4.0)
    parser.add_argument("--stop-ghz", type=float, default=10.0)
    parser.add_argument("--points", type=int, default=40)
    parser.add_argument("--adaptive-frequency-ghz", type=float, default=7.0)
    parser.add_argument("--setup", default="Setup_4to10G")
    parser.add_argument("--sweep", default="Sweep_4to10G_40pt")
    parser.add_argument("--sweep-type", choices=["Interpolating", "Discrete", "Fast"], default="Interpolating")
    parser.add_argument("--interpolation-tol-percent", type=float, default=0.5)
    parser.add_argument("--interpolation-max-solutions", type=int, default=120)
    parser.add_argument("--mesh-size-factor", type=float, default=2.0)
    parser.add_argument(
        "--enable-design-intersection-check",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "Set HFSS Design Settings > HFSS Meshing Method > Enable Design-level intersection checks. "
            "Use --no-enable-design-intersection-check for connector fixtures with intentional 3D component contact."
        ),
    )
    parser.add_argument("--port-type", choices=["aedt-edge", "edge-gap", "pin-gap", "circuit", "wave"], default="aedt-edge")
    parser.add_argument("--port-reference-name", default=None)
    parser.add_argument("--port-pec-launch-width", default="0.04mm")
    parser.add_argument("--port-horizontal-extent-factor", type=float, default=5.0)
    parser.add_argument("--port-vertical-extent-factor", type=float, default=3.0)
    parser.add_argument("--port-radial-extent-factor", type=float, default=0.0)
    parser.add_argument("--patch-edb-port-properties", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--skip-ports", action="store_true", help="Build layout, stackup, GND plane, and vias without creating ports.")
    parser.add_argument("--skip-port-number", type=int, action="append", default=[], choices=[1, 2], help="Skip creating one layout edge/pin port while keeping the other port.")
    parser.add_argument("--reference-ground-ports", dest="reference_ground_ports", action="store_true")
    parser.add_argument("--no-reference-ground-ports", dest="reference_ground_ports", action="store_false")
    parser.set_defaults(reference_ground_ports=False)
    parser.add_argument("--p1-edge", type=int, default=None, help="Override P1 signal edge. Default: infer from layout port coordinate.")
    parser.add_argument("--p2-edge", type=int, default=None, help="Override P2 signal edge. Default: infer from layout port coordinate.")
    parser.add_argument("--p1-ref-edge", type=int, default=None, help="Override P1 GND reference edge. Default: infer nearest boundary side.")
    parser.add_argument("--p2-ref-edge", type=int, default=None, help="Override P2 GND reference edge. Default: infer nearest boundary side.")
    parser.add_argument("--configure-extents", dest="configure_extents", action="store_true")
    parser.add_argument("--no-configure-extents", dest="configure_extents", action="store_false")
    parser.set_defaults(configure_extents=True)
    parser.add_argument("--diel-extent-type", default="BboxExtent")
    parser.add_argument("--diel-horizontal-padding", default="0.005")
    parser.add_argument("--diel-honor-primitives", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include-3d-subdesigns", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--airbox-extent-type", default="BboxExtent")
    parser.add_argument("--truncate-airbox-at-ground", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--airbox-horizontal-padding", default="0.15")
    parser.add_argument("--airbox-vertical-positive-padding", default="2")
    parser.add_argument("--airbox-vertical-negative-padding", default="2")
    parser.add_argument("--airbox-vertical-sync", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--open-region-type", default="Radiation")
    parser.add_argument("--use-radiation-boundary", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--pml-visible", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--open-region-frequency-ghz", type=float, default=5.0)
    parser.add_argument("--radiation-factor", type=float, default=0.0)
    parser.add_argument("--s2p", type=Path, default=None)
    parser.add_argument("--score-out", type=Path, default=None)
    parser.add_argument("--connector-params-json", type=Path, default=None, help="Connector launch params JSON for connector fixture manifests.")
    parser.add_argument("--connector-hfss-model-path", type=Path, default=None, help="Optional connector HFSS model path for Route C manifests.")
    parser.add_argument("--connector-hfss-model-version", default=None, help="Optional connector HFSS model version for Route C manifests.")
    parser.add_argument("--connector-hfss-model-hash", default=None, help="Optional connector HFSS model hash for Route C manifests.")
    parser.add_argument("--connector-port-mapping", default=None, help="Optional connector port mapping identifier or JSON string for Route C manifests.")
    parser.add_argument("--write-manifest", action="store_true", help="Write run_manifest.json, artifact_manifest.json, and state.json.")
    parser.add_argument("--project-id", default="bfp_6_8g_i7_fr4", help="Project id for run manifests.")
    parser.add_argument("--pipeline-id", default=None, help="Pipeline id for run manifests.")
    parser.add_argument("--round-id", default=None, help="Round id for run manifests. Default is inferred from paths.")
    parser.add_argument("--candidate-id", default=None, help="Candidate id for run manifests. Default uses layout_id.")
    parser.add_argument("--device-id", default="filter.interdigital", help="Device id for run manifests.")
    parser.add_argument("--profile-id", default="hfss3dlayout", help="Profile/backend id for run manifests.")
    parser.add_argument("--run-id", default=None, help="Explicit run id. Default is timestamped.")
    parser.add_argument("--run-dir", type=Path, default=None, help="Directory for manifest files.")
    parser.add_argument("--stackup-id", default=None, help="Stackup id for manifest. Default uses layout metadata substrate.")
    args = parser.parse_args()
    profile = get_hfss_profile(args.profile)
    args.profile_id = args.profile_id if args.profile_id != "hfss3dlayout" else profile.name
    args.workspace_dir = args.workspace_dir or profile.workspace_dir or Path(r"D:\Work\ADS\SIMADS_EM_PAR\HFSS_VERDICT")
    args.version = args.version or profile.version or AEDT_VERSION
    args.route = args.route or profile.route or "custom"
    args.stackup_config = args.stackup_config or profile.stackup_config
    args.non_graphical = args.non_graphical or profile.non_graphical
    args._hfss_profile = profile
    apply_hfss_route_defaults(args)
    return args


def main() -> None:
    args = parse_args()
    stackup_config = stackup_config_from_args(args)
    layout = load_layout(args.layout)
    summary = collect_layout_summary(layout)
    manifest_context = SimulationRunContext(
        project_id=args.project_id,
        round_id=args.round_id or infer_round_id(args.layout, args.out_dir, args.project_name),
        candidate_id=default_candidate_id(layout, args),
        profile_id=args.profile_id,
        simulator="hfss3dlayout",
        run_id=args.run_id,
        run_dir=args.run_dir,
        device_id=args.device_id,
        pipeline_id=args.pipeline_id,
    )
    run_id = manifest_context.resolved_run_id()
    run_dir = manifest_context.resolved_run_dir(REPO_ROOT, run_id)
    if args.dry_run:
        print(
            json.dumps(
                hfss_dry_run_payload(
                    args,
                    layout,
                    summary=summary,
                    stackup_config=stackup_config,
                    manifest_context=manifest_context,
                    run_id=run_id,
                    run_dir=run_dir,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    started = time.monotonic()
    if args.write_manifest:
        write_hfss_manifests(
            args,
            layout,
            run_id=run_id,
            run_dir=run_dir,
            status="running",
            stage="planned",
            elapsed_s=0.0,
        )
    try:
        result = run_hfss(args)
    except BaseException as exc:
        if args.write_manifest:
            write_hfss_manifests(
                args,
                layout,
                run_id=run_id,
                run_dir=run_dir,
                status="failed",
                stage="failed",
                elapsed_s=time.monotonic() - started,
                error=exc,
            )
        raise
    if args.write_manifest:
        manifest_paths = write_hfss_manifests(
            args,
            layout,
            run_id=run_id,
            run_dir=run_dir,
            status="completed",
            stage=completed_hfss_stage(args, result),
            elapsed_s=time.monotonic() - started,
            result=result,
        )
        result["run_id"] = run_id
        result["run_dir"] = str(run_dir)
        result["manifest_paths"] = {key: str(path) for key, path in manifest_paths.items()}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


