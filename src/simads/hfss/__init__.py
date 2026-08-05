"""HFSS automation helpers for SIMADS."""

from simads.hfss.artifacts import (
    HFSS_PROJECT_ACTION_ADD,
    HFSS_PROJECT_ACTION_NEW,
    HFSS_PROJECT_ACTIONS,
    HFSS_PROJECT_MODEL_PER_DESIGN,
    HFSS_PROJECT_MODEL_SINGLE_AEDT,
    HFSS_PROJECT_MODELS,
    default_project_name,
    expected_hfss_outputs,
    resolve_project_path,
)
from simads.hfss.build import HfssLayoutBuildResult, build_hfss_layout_project
from simads.hfss.layout import GeometryBuildOptions
from simads.hfss.layout_io import collect_layout_summary, configured_layout_id, load_layout
from simads.hfss.ports import resolve_gnd_boundary, resolve_port_edges
from simads.hfss.port_plans import ConnectorPinPortPlan, execute_connector_pin_port_plan
from simads.hfss.connector_contract import connector_fixture_metadata, connector_port_reference_name, is_connector_fixture
from simads.hfss.manifest import build_hfss_manifest_payload, write_hfss_manifests
from simads.hfss.plans import (
    RELIABLE_HFSS_ROUTE,
    Hfss3dLayoutVerdictPlan,
    apply_hfss_route_defaults,
    build_reliable_hfss_verdict_plan,
)
from simads.hfss.solve import HfssSolveExportResult, solve_and_export_hfss
from simads.hfss.session import Hfss3dLayoutSession, Hfss3dLayoutSessionConfig, open_hfss3dlayout_session
from simads.hfss.connector import (
    FIXTURE_TYPE,
    SINGLE_CONNECTOR_FIXTURE_TYPE,
    ConnectorLaunchParams,
    assert_connector_layout_valid,
    build_layout as build_connector_layout,
    build_single_connector_layout,
    params_with_stackup_config as connector_params_with_stackup_config,
    validate_connector_layout,
)

__all__ = [
    "Hfss3dLayoutVerdictPlan",
    "HfssLayoutBuildResult",
    "HfssSolveExportResult",
    "Hfss3dLayoutSession",
    "Hfss3dLayoutSessionConfig",
    "GeometryBuildOptions",
    "ConnectorLaunchParams",
    "ConnectorPinPortPlan",
    "connector_fixture_metadata",
    "connector_port_reference_name",
    "is_connector_fixture",
    "FIXTURE_TYPE",
    "SINGLE_CONNECTOR_FIXTURE_TYPE",
    "RELIABLE_HFSS_ROUTE",
    "HFSS_PROJECT_ACTION_ADD",
    "HFSS_PROJECT_ACTION_NEW",
    "HFSS_PROJECT_ACTIONS",
    "HFSS_PROJECT_MODEL_PER_DESIGN",
    "HFSS_PROJECT_MODEL_SINGLE_AEDT",
    "HFSS_PROJECT_MODELS",
    "apply_hfss_route_defaults",
    "assert_connector_layout_valid",
    "build_hfss_layout_project",
    "build_hfss_manifest_payload",
    "build_connector_layout",
    "build_single_connector_layout",
    "build_reliable_hfss_verdict_plan",
    "connector_params_with_stackup_config",
    "collect_layout_summary",
    "configured_layout_id",
    "default_project_name",
    "execute_connector_pin_port_plan",
    "expected_hfss_outputs",
    "load_layout",
    "open_hfss3dlayout_session",
    "resolve_gnd_boundary",
    "resolve_project_path",
    "resolve_port_edges",
    "solve_and_export_hfss",
    "validate_connector_layout",
    "write_hfss_manifests",
]
