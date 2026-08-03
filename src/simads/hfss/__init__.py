"""HFSS automation helpers for SIMADS."""

from simads.hfss.artifacts import default_project_name, expected_hfss_outputs, resolve_project_path
from simads.hfss.build import HfssLayoutBuildResult, build_hfss_layout_project
from simads.hfss.layout import GeometryBuildOptions
from simads.hfss.layout_io import collect_layout_summary, configured_layout_id, load_layout
from simads.hfss.ports import resolve_gnd_boundary, resolve_port_edges
from simads.hfss.plans import (
    RELIABLE_HFSS_ROUTE,
    Hfss3dLayoutVerdictPlan,
    apply_hfss_route_defaults,
    build_reliable_hfss_verdict_plan,
)
from simads.hfss.solve import HfssSolveExportResult, solve_and_export_hfss

__all__ = [
    "Hfss3dLayoutVerdictPlan",
    "HfssLayoutBuildResult",
    "HfssSolveExportResult",
    "GeometryBuildOptions",
    "RELIABLE_HFSS_ROUTE",
    "apply_hfss_route_defaults",
    "build_hfss_layout_project",
    "build_reliable_hfss_verdict_plan",
    "collect_layout_summary",
    "configured_layout_id",
    "default_project_name",
    "expected_hfss_outputs",
    "load_layout",
    "resolve_gnd_boundary",
    "resolve_project_path",
    "resolve_port_edges",
    "solve_and_export_hfss",
]
