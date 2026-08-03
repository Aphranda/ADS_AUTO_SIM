"""HFSS 3D Layout planning helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from simads.common import CommandPlan

RELIABLE_HFSS_ROUTE = "hfss3dlayout_aedt_edge_gap_gnd_port_edges"


@dataclass(frozen=True)
class Hfss3dLayoutVerdictPlan:
    layout: Path
    workspace_dir: Path
    out_dir: Path
    project_name: str
    design: str = "I7_FR4_HFSS_VERDICT"
    version: str = "2026.1"
    port_type: str = "aedt-edge"
    gnd_boundary_mode: str = "port-edges"
    start_ghz: float = 4.0
    stop_ghz: float = 10.0
    points: int = 40
    sweep_type: str = "Interpolating"
    non_graphical: bool = True
    build_only: bool = False

    def to_manifest(self) -> dict[str, object]:
        return {
            "layout": str(self.layout),
            "workspace_dir": str(self.workspace_dir),
            "out_dir": str(self.out_dir),
            "project_name": self.project_name,
            "design": self.design,
            "version": self.version,
            "port_type": self.port_type,
            "gnd_boundary_mode": self.gnd_boundary_mode,
            "start_ghz": self.start_ghz,
            "stop_ghz": self.stop_ghz,
            "points": self.points,
            "sweep_type": self.sweep_type,
            "non_graphical": self.non_graphical,
            "build_only": self.build_only,
        }


def build_reliable_hfss_verdict_plan(
    *,
    layout: Path,
    workspace_dir: Path,
    out_dir: Path,
    project_name: str,
    build_only: bool = False,
    start_ghz: float = 4.0,
    stop_ghz: float = 10.0,
    points: int = 40,
) -> Hfss3dLayoutVerdictPlan:
    """Build the currently validated HFSS route.

    Reliable route:
    - HFSS 3D Layout.
    - AEDT-native edge ports.
    - Gap/Vertical port properties.
    - GND left/right edges aligned to P1/P2 port cross sections.
    """
    return Hfss3dLayoutVerdictPlan(
        layout=layout,
        workspace_dir=workspace_dir,
        out_dir=out_dir,
        project_name=project_name,
        build_only=build_only,
        start_ghz=start_ghz,
        stop_ghz=stop_ghz,
        points=points,
    )


def apply_hfss_route_defaults(args: object) -> str:
    route = str(getattr(args, "route", "custom") or "custom")
    if route == "custom":
        return route
    if route not in {"reliable", RELIABLE_HFSS_ROUTE}:
        raise ValueError(f"unsupported HFSS route: {route}")
    args.route = RELIABLE_HFSS_ROUTE
    args.port_type = "aedt-edge"
    args.gnd_boundary_mode = "port-edges"
    args.configure_extents = True
    args.reference_ground_ports = False
    args.patch_edb_port_properties = True
    return RELIABLE_HFSS_ROUTE


def build_hfss_verdict_command(
    plan: Hfss3dLayoutVerdictPlan,
    *,
    python: Path,
    script: Path,
) -> CommandPlan:
    args = [
        "--layout",
        str(plan.layout),
        "--workspace-dir",
        str(plan.workspace_dir),
        "--out-dir",
        str(plan.out_dir),
        "--project-name",
        plan.project_name,
        "--design",
        plan.design,
        "--version",
        plan.version,
        "--port-type",
        plan.port_type,
        "--gnd-boundary-mode",
        plan.gnd_boundary_mode,
        "--start-ghz",
        f"{plan.start_ghz:g}",
        "--stop-ghz",
        f"{plan.stop_ghz:g}",
        "--points",
        str(plan.points),
        "--sweep-type",
        plan.sweep_type,
    ]
    if plan.non_graphical:
        args.append("--non-graphical")
    if plan.build_only:
        args.append("--build-only")
    return CommandPlan("hfss3dlayout_filter_verdict", python, script, tuple(args), cwd=script.parents[2])
