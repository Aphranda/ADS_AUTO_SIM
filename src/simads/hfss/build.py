"""Build HFSS 3D Layout projects from SIM layout JSON."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from simads.config import StackupConfig
from simads.hfss.layout import GeometryBuildOptions, create_geometry
from simads.hfss.ports import create_ports, resolve_gnd_boundary
from simads.hfss.stackup import (
    configure_hfss_extents,
    ensure_material,
    ensure_stackup_materials,
    reset_stackup,
    reset_stackup_from_config,
)


@dataclass(frozen=True)
class HfssLayoutBuildResult:
    project: str
    design: str
    geometry_count: int
    gnd_boundary: dict[str, Any] | None
    ports: list[str]
    port_edges: dict[str, Any]
    extents_configured: bool
    stackup_config: dict[str, Any] | None
    setup: str
    sweep: str
    build_only: bool
    saved: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _legacy_stackup_values(args: argparse.Namespace, metadata: dict[str, Any]) -> tuple[float, float, float, float]:
    er = float(args.er if args.er is not None else metadata.get("er", 4.6))
    loss_tangent = float(args.loss_tangent if args.loss_tangent is not None else 0.02)
    core_h_mm = float(args.substrate_height_mm or metadata.get("dielectric_height_mm", 0.21))
    cu_t_mm = float(args.copper_thickness_mm or metadata.get("copper_thickness_mm", 0.035))
    return er, loss_tangent, core_h_mm, cu_t_mm


def build_hfss_layout_project(
    app: Any,
    layout: dict[str, Any],
    args: argparse.Namespace,
    *,
    project_path: Path,
    stackup_config: StackupConfig | None = None,
) -> HfssLayoutBuildResult:
    metadata = layout.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    app.modeler.model_units = "mm"
    if stackup_config is None:
        er, loss_tangent, core_h_mm, cu_t_mm = _legacy_stackup_values(args, metadata)
        ensure_material(app, er, loss_tangent)
        reset_stackup(app, core_h_mm, cu_t_mm)
    else:
        ensure_stackup_materials(app, stackup_config)
        reset_stackup_from_config(app, stackup_config)

    gnd_boundary = resolve_gnd_boundary(layout, args)
    geometry = create_geometry(app, layout, GeometryBuildOptions.from_args(args))
    extents_configured = configure_hfss_extents(app, args)
    if args.skip_ports:
        ports: list[str] = []
        port_edges: dict[str, Any] = {}
    else:
        ports, port_edges = create_ports(app, layout, args)

    setup = app.create_setup(
        name=args.setup,
        MeshSizeFactor=args.mesh_size_factor,
        SingleFrequencyDataList__AdaptiveFrequency=f"{args.adaptive_frequency_ghz}GHz",
    )
    sweep = app.create_linear_count_sweep(
        setup=args.setup,
        unit="GHz",
        start_frequency=args.start_ghz,
        stop_frequency=args.stop_ghz,
        num_of_freq_points=args.points,
        name=args.sweep,
        save_fields=False,
        sweep_type=args.sweep_type,
        interpolation_tol_percent=args.interpolation_tol_percent,
        interpolation_max_solutions=args.interpolation_max_solutions,
    )
    saved = app.save_project(str(project_path), overwrite=True)

    return HfssLayoutBuildResult(
        project=str(project_path),
        design=getattr(args, "design", "HFSSDesign"),
        geometry_count=len(geometry),
        gnd_boundary=gnd_boundary,
        ports=ports,
        port_edges=port_edges,
        extents_configured=extents_configured,
        stackup_config=stackup_config.to_dict() if stackup_config is not None else None,
        setup=getattr(setup, "name", args.setup),
        sweep=getattr(sweep, "name", args.sweep),
        build_only=args.build_only,
        saved=bool(saved),
    )


__all__ = ["HfssLayoutBuildResult", "build_hfss_layout_project"]
