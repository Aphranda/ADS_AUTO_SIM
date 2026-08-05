"""HFSS simulation manifest construction helpers."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from simads.config import StackupConfig, load_stackup_config
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
from simads.hfss.artifacts import expected_hfss_outputs
from simads.hfss.connector_contract import connector_fixture_metadata, is_connector_fixture
from simads.hfss.layout_io import collect_layout_summary, configured_layout_id
from simads.hfss.ports import BOTTOM_LAYER, TOP_LAYER, resolve_gnd_boundary, resolve_port_edges
from simads.hfss.stackup import DIELECTRIC_LAYER, FR4_MATERIAL


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


def manifest_stackup(args: argparse.Namespace, metadata: dict[str, Any]) -> StackupSpec:
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
    stackup = manifest_stackup(args, metadata)
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
    if is_connector_fixture(layout):
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


__all__ = [
    "build_hfss_manifest_payload",
    "completed_hfss_stage",
    "default_candidate_id",
    "infer_round_id",
    "manifest_stackup",
    "stackup_config_from_args",
    "write_hfss_manifests",
]
