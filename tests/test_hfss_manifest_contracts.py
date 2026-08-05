from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from simads.hfss.connector import SINGLE_CONNECTOR_FIXTURE_TYPE
from simads.hfss.connector_contract import connector_fixture_metadata
from simads.hfss.manifest import build_hfss_manifest_payload
from simads.hfss.workflow import build_hfss_manifest_payload as workflow_manifest_payload


def _args(layout_path: Path, out_dir: Path) -> Namespace:
    return Namespace(
        layout=layout_path,
        out_dir=out_dir,
        workspace_dir=out_dir / "workspace",
        project=None,
        project_name=None,
        project_model="per_design_project",
        project_action="new",
        reuse_project=False,
        design="CONNECTOR_UNIT",
        version="2026.1",
        non_graphical=True,
        keep_open=False,
        build_only=True,
        dry_run=True,
        route="custom",
        substrate_height_mm=None,
        copper_thickness_mm=None,
        stackup_config=None,
        er=None,
        loss_tangent=None,
        gnd_boundary_mode="em-boundary",
        start_ghz=4.0,
        stop_ghz=10.0,
        points=40,
        adaptive_frequency_ghz=7.0,
        setup="Setup_4to10G",
        sweep="Sweep_4to10G_40pt",
        sweep_type="Interpolating",
        s2p=None,
        score_out=None,
        port_type="edge-gap",
        port_reference_name=None,
        enable_design_intersection_check=None,
        skip_ports=False,
        skip_port_number=[],
        reference_ground_ports=True,
        p1_edge=None,
        p2_edge=None,
        p1_ref_edge=None,
        p2_ref_edge=None,
        configure_extents=True,
        project_id="connector_project",
        round_id="round1",
        candidate_id=None,
        device_id="fixture.microstrip_connector",
        profile_id="home",
        run_dir=None,
        stackup_id=None,
        connector_params_json=None,
        connector_hfss_model_path=None,
        connector_hfss_model_version=None,
        connector_hfss_model_hash=None,
        connector_port_mapping=None,
    )


def _layout() -> dict:
    return {
        "layout_id": "connector_unit",
        "units": "mm",
        "metadata": {
            "fixture_type": SINGLE_CONNECTOR_FIXTURE_TYPE,
            "connector_route": "route_a",
            "connector_type": "edge_launch",
            "line_w_mm": 0.3175,
            "line_l_mm": 30.0,
            "reference_ground_layer": "ETCH_INNER1",
            "ground_plane_name": "hfss_ground_plane",
            "port_deembed_mm": 0.0,
        },
        "ports": [
            {"name": "P1", "number": 1, "x": 0.0, "y": 0.0, "width": 1.2, "layer": "cond", "orientation_deg": 180.0},
            {"name": "P2", "number": 2, "x": 30.0, "y": 0.0, "width": 0.3175, "layer": "cond", "orientation_deg": 0.0},
        ],
        "shapes": [
            {"kind": "boundary", "layer": "EM_BOUNDARY", "name": "em_boundary", "x": -1.0, "y": -4.0, "w": 32.0, "h": 8.0},
            {"kind": "rect", "layer": "cond", "name": "input_feed", "x": 0.0, "y": -0.6, "w": 2.0, "h": 1.2},
            {"kind": "rect", "layer": "cond", "name": "output_feed", "x": 28.0, "y": -0.16, "w": 2.0, "h": 0.32},
        ],
    }


def test_connector_contract_derives_reference_and_params_path(tmp_path: Path) -> None:
    layout_path = tmp_path / "connector_unit_layout.json"
    params_path = tmp_path / "connector_unit_params.json"
    params_path.write_text("{}", encoding="utf-8")
    args = _args(layout_path, tmp_path)

    metadata = connector_fixture_metadata(args, _layout())

    assert metadata["fixture_type"] == SINGLE_CONNECTOR_FIXTURE_TYPE
    assert metadata["connector_params_json"] == str(params_path)
    assert metadata["connector_port_contract"]["reference_name"] == "GND:ETCH_INNER1:hfss_ground_plane"
    assert metadata["connector_port_contract"]["renormalize_impedance_ohm"] == 50.0


def test_manifest_builder_is_split_but_workflow_import_remains_compatible(tmp_path: Path) -> None:
    layout_path = tmp_path / "connector_unit_layout.json"
    (tmp_path / "connector_unit_params.json").write_text("{}", encoding="utf-8")
    args = _args(layout_path, tmp_path)
    layout = _layout()

    payload = build_hfss_manifest_payload(args, layout, run_id="run1")
    workflow_payload = workflow_manifest_payload(args, layout, run_id="run1")

    assert workflow_payload.inputs == payload.inputs
    assert payload.inputs["connector_params_json"].endswith("connector_unit_params.json")
    assert payload.flags["fixture_type"] == SINGLE_CONNECTOR_FIXTURE_TYPE
    assert payload.extra["connector_port_contract"]["reference_name"] == "GND:ETCH_INNER1:hfss_ground_plane"
