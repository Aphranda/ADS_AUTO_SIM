import json
from argparse import Namespace
from dataclasses import replace
from pathlib import Path

import pytest

from simads.runtime import SimulationRunContext
from simads.config import load_stackup_config
from simads.geometry import to_dict, validate_layout_contract
from simads.hfss.connector import (
    BASELINE_FIXTURE_TYPE,
    FIXTURE_TYPE,
    SINGLE_CONNECTOR_FIXTURE_TYPE,
    ConnectorLaunchParams,
    assert_connector_layout_valid,
    board_height,
    build_layout,
    build_microstrip_baseline_layout,
    build_single_connector_layout,
    launch_len,
    load_fixture_type,
    params_with_total_len,
    params_with_stackup_config,
    port_locations,
    total_len,
    validate_connector_layout,
    write_fixture_outputs,
    write_outputs,
)
from simads.hfss.layout_io import collect_layout_summary
from simads.hfss.layout import GeometryBuildOptions, create_geometry
from simads.hfss.workflow import build_hfss_manifest_payload, hfss_dry_run_payload, write_hfss_manifests


class Obj:
    def __init__(self, name: str) -> None:
        self.name = name
        self.negative = False


class FakeModeler:
    def __init__(self) -> None:
        self.calls = []

    def create_rectangle(self, layer, origin, size, name, net):
        self.calls.append(("rect", layer, origin, size, name, net))
        return Obj(name)

    def create_polygon(self, layer, points, units, name, net):
        self.calls.append(("polygon", layer, points, units, name, net))
        return Obj(name)

    def create_circle(self, layer, x, y, radius, name, net):
        self.calls.append(("circle", layer, x, y, radius, name, net))
        return Obj(name)

    def create_via(self, x, y, hole_diam, top_layer, bot_layer, name, net):
        self.calls.append(("via", x, y, hole_diam, top_layer, bot_layer, name, net))
        return Obj(name)

    def subtract(self, blank, tools, keep_originals=False):
        self.calls.append(("subtract", getattr(blank, "name", str(blank)), [getattr(tool, "name", str(tool)) for tool in tools], keep_originals))
        return True


class FakeApp:
    def __init__(self) -> None:
        self.modeler = FakeModeler()


def mm_value(value):
    if isinstance(value, str) and value.endswith("mm"):
        return float(value[:-2])
    return float(value)


def stackup_params(**kwargs) -> ConnectorLaunchParams:
    stackup_path = Path("config/stackups/JLC04161H_7628_1P6MM.json")
    return params_with_stackup_config(
        ConnectorLaunchParams(**kwargs),
        load_stackup_config(stackup_path),
        config_path=stackup_path,
    )


def hfss_args(layout_path: Path, out_dir: Path, **overrides) -> Namespace:
    data = {
        "layout": layout_path,
        "out_dir": out_dir,
        "workspace_dir": out_dir / "workspace",
        "project": None,
        "project_name": None,
        "project_model": "per_design_project",
        "project_action": "new",
        "reuse_project": False,
        "design": "CONNECTOR_SMOKE",
        "version": "2026.1",
        "non_graphical": True,
        "keep_open": False,
        "build_only": True,
        "dry_run": True,
        "route": "custom",
        "substrate_height_mm": None,
        "copper_thickness_mm": None,
        "stackup_config": Path("config/stackups/JLC04161H_7628_1P6MM.json"),
        "er": None,
        "loss_tangent": None,
        "gnd_boundary_mode": "port-edges",
        "start_ghz": 4.0,
        "stop_ghz": 10.0,
        "points": 40,
        "adaptive_frequency_ghz": 7.0,
        "setup": "Setup_4to10G",
        "sweep": "Sweep_4to10G_40pt",
        "sweep_type": "Interpolating",
        "port_type": "edge-gap",
        "port_reference_name": None,
        "port_pec_launch_width": "0.04mm",
        "port_horizontal_extent_factor": 5.0,
        "port_vertical_extent_factor": 3.0,
        "port_radial_extent_factor": 0.0,
        "enable_design_intersection_check": None,
        "skip_ports": False,
        "reference_ground_ports": True,
        "p1_edge": None,
        "p2_edge": None,
        "p1_ref_edge": None,
        "p2_ref_edge": None,
        "configure_extents": True,
        "diel_extent_type": "BboxExtent",
        "diel_horizontal_padding": "0.005",
        "diel_honor_primitives": True,
        "include_3d_subdesigns": False,
        "airbox_extent_type": "BboxExtent",
        "truncate_airbox_at_ground": False,
        "airbox_horizontal_padding": "0.15",
        "airbox_vertical_positive_padding": "2",
        "airbox_vertical_negative_padding": "2",
        "airbox_vertical_sync": True,
        "open_region_type": "Radiation",
        "use_radiation_boundary": True,
        "open_region_frequency_ghz": 5.0,
        "radiation_factor": 0.0,
        "s2p": None,
        "score_out": None,
        "write_manifest": True,
        "project_id": "connector_project",
        "round_id": "round1",
        "candidate_id": None,
        "device_id": "fixture.microstrip_connector",
        "profile_id": "home",
        "run_id": "run1",
        "run_dir": None,
        "stackup_id": None,
        "connector_params_json": None,
        "connector_hfss_model_path": None,
        "connector_hfss_model_version": None,
        "connector_hfss_model_hash": None,
        "connector_port_mapping": None,
        "skip_port_number": [],
    }
    data.update(overrides)
    return Namespace(**data)


def test_microstrip_connector_layout_records_stackup_and_fixture_metadata() -> None:
    params = stackup_params(name="connector_smoke_a")
    layout = build_layout(params)
    layout_json = to_dict(layout)

    assert layout.metadata["fixture_type"] == FIXTURE_TYPE
    assert layout.metadata["connector_route"] == "route_a_2p5d_launch_surrogate"
    assert layout.metadata["stackup_id"] == "JLC04161H_7628_1P6MM"
    assert layout.metadata["signal_layer"] == "ETCH_TOP"
    assert layout.metadata["reference_ground_layer"] == "ETCH_INNER1"
    assert layout.metadata["line_l_mm"] == params.line_l_mm
    assert layout.ports[0].x == 0.0
    assert layout.ports[1].x == total_len(params)
    assert layout_json["metadata"]["connector_region_bbox_mm"]["P1"][0] == 0.0

    checks = validate_layout_contract(
        layout_json,
        metal_layer="cond",
        via_layer="pcvia1",
        layer_map_version="microstrip-connector-logical-v1",
    )
    assert all(check.ok for check in checks), [check for check in checks if not check.ok]


def test_microstrip_connector_smoke_variants_pass_connector_drc(tmp_path: Path) -> None:
    variants = [
        stackup_params(name="connector_smoke_a"),
        stackup_params(name="connector_smoke_b", pin_pad_w_mm=1.0, taper_l_mm=2.0, via_count=3),
        stackup_params(name="connector_smoke_c", line_w_mm=0.40, gnd_clearance_mm=0.36, via_pitch_mm=0.95),
    ]

    for params in variants:
        layout = build_layout(params)
        assert all(check.ok for check in validate_connector_layout(layout, params))
        outputs = write_outputs(params, tmp_path)
        assert outputs["layout_json"].exists()
        assert outputs["params"].exists()
        assert outputs["svg"].exists()
        svg_text = outputs["svg"].read_text(encoding="utf-8")
        assert "L1 ETCH_TOP" in svg_text
        assert "L2 ETCH_INNER1" in svg_text
        payload = json.loads(outputs["params"].read_text(encoding="utf-8"))
        assert payload["fixture_type"] == FIXTURE_TYPE
        assert payload["ports"]["P1"] == list(port_locations(params)[0])
        assert payload["ports"]["P2"] == list(port_locations(params)[1])


def test_single_connector_layer_review_svg_does_not_duplicate_l2_ground(tmp_path: Path) -> None:
    params = stackup_params(
        name="se30_ref1p5_l3solid",
        pin_pad_w_mm=0.95,
        pin_pad_l_mm=2.8,
        taper_l_mm=3.6,
        taper_w_start_mm=0.9,
        launch_ground_gap_mm=1.5,
        launch_ground_via_enabled=False,
        connector_ground_foot_via_enabled=True,
        line_l_mm=23.1,
        fence_offset_mm=0.75,
        l2_cutout_enabled=True,
        l2_cutout_shape="rect",
        l2_cutout_w_mm=1.6,
        l2_cutout_l_mm=3.8,
        l2_cutout_offset_x_mm=0.15,
        l3_cutout_enabled=False,
        l3_cutout_shape="none",
        l3_ground_enabled=True,
        reference_ground_extend_right_mm=1.5,
        l3_ground_extend_right_mm=1.5,
        l4_ground_enabled=True,
        l4_ground_extend_right_mm=1.5,
    )

    outputs = write_fixture_outputs(params, tmp_path, fixture_type=SINGLE_CONNECTOR_FIXTURE_TYPE)
    svg_text = outputs["svg"].read_text(encoding="utf-8")

    assert "L1 ETCH_TOP" in svg_text
    assert "L2 ETCH_INNER1" in svg_text
    assert "L3 ETCH_INNER2" in svg_text
    assert "L4 ETCH_BOTTOM" in svg_text
    assert "GND" not in svg_text
    assert svg_text.count("ETCH_INNER1</text>") == 1


def test_microstrip_connector_layout_is_compatible_with_hfss_geometry_builder() -> None:
    params = stackup_params(name="connector_hfss_builder_smoke", via_count=2)
    layout = to_dict(build_layout(params))
    app = FakeApp()

    names = create_geometry(
        app,
        layout,
        GeometryBuildOptions(
            gnd_boundary_mode="port-edges",
            signal_layer="ETCH_TOP",
            reference_ground_layer="ETCH_INNER1",
            via_top_layer="ETCH_TOP",
            via_bottom_layer="ETCH_BOTTOM",
            ground_plane_name="hfss_ground_plane",
        ),
    )

    assert "hfss_ground_plane" in names
    assert "input_feed" in names
    assert "output_feed" in names
    assert "center_line_top_ground" in names
    assert any(
        call[0] == "rect"
        and call[1] == "ETCH_TOP"
        and call[4] == "input_feed"
        and call[5] == "IN"
        and mm_value(call[2][0]) == pytest.approx(0.0)
        and mm_value(call[2][1]) == pytest.approx(-params.pin_pad_w_mm / 2.0)
        and mm_value(call[3][0]) == pytest.approx(params.pin_pad_l_mm)
        and mm_value(call[3][1]) == pytest.approx(params.pin_pad_w_mm)
        for call in app.modeler.calls
    )
    assert any(call[0] == "rect" and call[4] == "center_line_top_ground" and call[5] == "GND" for call in app.modeler.calls)
    assert any(call[0] == "via" and call[4] == "ETCH_TOP" and call[5] == "ETCH_BOTTOM" for call in app.modeler.calls)


def test_microstrip_baseline_layout_is_connector_launch_free_and_hfss_compatible(tmp_path: Path) -> None:
    params = stackup_params(name="connector_baseline_probe", via_count=2)
    layout = build_microstrip_baseline_layout(params)
    layout_json = to_dict(layout)
    app = FakeApp()

    names = create_geometry(
        app,
        layout_json,
        GeometryBuildOptions(
            gnd_boundary_mode="port-edges",
            signal_layer="ETCH_TOP",
            reference_ground_layer="ETCH_INNER1",
            via_top_layer="ETCH_TOP",
            via_bottom_layer="ETCH_BOTTOM",
            ground_plane_name="hfss_ground_plane",
        ),
    )
    outputs = write_fixture_outputs(params, tmp_path, fixture_type=BASELINE_FIXTURE_TYPE)
    params_payload = json.loads(outputs["params"].read_text(encoding="utf-8"))

    assert layout.metadata["fixture_type"] == BASELINE_FIXTURE_TYPE
    assert layout.metadata["baseline_for_fixture_type"] == FIXTURE_TYPE
    assert not any(shape.get("metadata", {}).get("role") == "connector_launch_signal" for shape in layout_json["shapes"])
    assert len([shape for shape in layout_json["shapes"] if shape["kind"] == "via"]) > 0
    assert any(shape["name"] == "line_top_ground" and shape["metadata"]["net"] == "GND" for shape in layout_json["shapes"])
    assert "input_feed" in names
    assert "output_feed" in names
    assert params_payload["fixture_type"] == BASELINE_FIXTURE_TYPE


def test_microstrip_connector_can_emit_l2_cutout_and_hi_z_series() -> None:
    params = stackup_params(
        name="connector_l2_hiz_probe",
        pin_pad_w_mm=1.0,
        pin_pad_l_mm=2.8,
        taper_w_start_mm=0.9,
        taper_l_mm=3.0,
        l2_cutout_enabled=True,
        l2_cutout_shape="rect",
        l2_cutout_w_mm=1.6,
        l2_cutout_l_mm=3.6,
        l2_cutout_offset_x_mm=0.25,
        series_hi_z_enabled=True,
        series_hi_z_w_mm=0.24,
        series_hi_z_l_mm=0.6,
    )
    layout = build_layout(params)
    layout_json = to_dict(layout)
    app = FakeApp()

    names = create_geometry(
        app,
        layout_json,
        GeometryBuildOptions(
            gnd_boundary_mode="port-edges",
            signal_layer="ETCH_TOP",
            reference_ground_layer="ETCH_INNER1",
            via_top_layer="ETCH_TOP",
            via_bottom_layer="ETCH_BOTTOM",
            ground_plane_name="hfss_ground_plane",
        ),
    )

    assert all(check.ok for check in validate_connector_layout(layout, params))
    assert any(shape["kind"] == "reference_ground_cutout" for shape in layout_json["shapes"])
    l2_planes = [
        shape
        for shape in layout_json["shapes"]
        if shape["kind"] == "reference_ground_plane" and shape.get("metadata", {}).get("target_layer") == "reference_ground_layer"
    ]
    assert len(l2_planes) > 1
    assert any(shape["name"] == "hfss_ground_plane" for shape in l2_planes)
    assert "input_series_hi_z" in names
    assert "output_series_hi_z" in names
    assert "hfss_ground_plane" in names
    assert "p1_l2_cutout_rect" not in names
    assert not any(
        call[0] == "rect"
        and call[1] == "ETCH_INNER1"
        and call[3][0] == pytest.approx(total_len(params))
        and call[3][1] == pytest.approx(board_height(params))
        for call in app.modeler.calls
    )
    assert not any(call[0] == "subtract" for call in app.modeler.calls)


def test_connector_svg_renders_l2_as_positive_ground_with_cutout_window(tmp_path: Path) -> None:
    params = stackup_params(
        name="connector_l2_svg_probe",
        l2_cutout_enabled=True,
        l2_cutout_shape="rect",
        l2_cutout_w_mm=1.4,
        l2_cutout_l_mm=3.0,
        l2_cutout_offset_x_mm=0.3,
    )

    outputs = write_fixture_outputs(params, tmp_path, fixture_type=SINGLE_CONNECTOR_FIXTURE_TYPE)
    svg_text = outputs["svg"].read_text(encoding="utf-8")

    assert "L1 ETCH_TOP" in svg_text
    assert "L2 ETCH_INNER1" in svg_text
    assert 'fill="#16a34a"' in svg_text
    assert 'fill="#ffffff"' in svg_text
    assert 'fill="none" stroke="#dc2626"' in svg_text


def test_single_connector_tapered_l2_cutout_materializes_positive_polygon_ground(tmp_path: Path) -> None:
    params = stackup_params(
        name="se30_l2_taper_probe",
        pin_pad_w_mm=0.95,
        pin_pad_l_mm=2.8,
        taper_l_mm=3.6,
        taper_w_start_mm=0.9,
        launch_ground_gap_mm=1.5,
        launch_ground_via_enabled=False,
        connector_ground_foot_via_enabled=True,
        line_l_mm=23.1,
        fence_offset_mm=0.75,
        l2_cutout_enabled=True,
        l2_cutout_shape="tapered",
        l2_cutout_w_mm=1.6,
        l2_cutout_l_mm=3.8,
        l2_cutout_offset_x_mm=0.15,
        l2_cutout_taper_l_mm=3.6,
        l3_cutout_enabled=False,
        l3_cutout_shape="none",
        l3_ground_enabled=True,
        reference_ground_extend_right_mm=1.5,
        l3_ground_extend_right_mm=1.5,
        l4_ground_enabled=True,
        l4_ground_extend_right_mm=1.5,
    )
    layout = build_single_connector_layout(params)
    layout_json = to_dict(layout)
    app = FakeApp()

    names = create_geometry(
        app,
        layout_json,
        GeometryBuildOptions(
            gnd_boundary_mode="port-edges",
            signal_layer="ETCH_TOP",
            reference_ground_layer="ETCH_INNER1",
            via_top_layer="ETCH_TOP",
            via_bottom_layer="ETCH_BOTTOM",
            ground_plane_name="hfss_ground_plane",
        ),
    )
    outputs = write_fixture_outputs(params, tmp_path, fixture_type=SINGLE_CONNECTOR_FIXTURE_TYPE)
    svg_text = outputs["svg"].read_text(encoding="utf-8")

    l2_cutouts = [
        shape
        for shape in layout_json["shapes"]
        if shape["kind"] == "reference_ground_cutout" and shape.get("metadata", {}).get("target_layer") == "reference_ground_layer"
    ]
    l2_planes = [
        shape
        for shape in layout_json["shapes"]
        if shape["kind"] == "reference_ground_plane" and shape.get("metadata", {}).get("target_layer") == "reference_ground_layer"
    ]

    assert any("points" in shape and shape["name"] == "p1_l2_cutout_tapered" for shape in l2_cutouts)
    assert any("points" in shape for shape in l2_planes)
    assert "hfss_ground_plane" in names
    assert any(call[0] == "polygon" and call[1] == "ETCH_INNER1" and call[4] == "hfss_ground_plane" for call in app.modeler.calls)
    assert not any(call[0] == "subtract" for call in app.modeler.calls)
    assert "L1 ETCH_TOP" in svg_text
    assert "L2 ETCH_INNER1" in svg_text
    assert "L3 ETCH_INNER2" in svg_text
    assert "L4 ETCH_BOTTOM" in svg_text
    assert "GND" not in svg_text
    assert svg_text.count("ETCH_INNER1</text>") == 1


def test_microstrip_baseline_can_target_exact_total_length() -> None:
    params = stackup_params(name="connector_baseline_100mm_probe", line_l_mm=18.0)
    exact = params_with_total_len(params, 100.0)
    layout = build_microstrip_baseline_layout(exact)

    assert exact.line_l_mm == pytest.approx(100.0 - 2.0 * launch_len(params))
    assert layout.ports[0].x == 0.0
    assert layout.ports[1].x == pytest.approx(100.0)
    assert layout.metadata["line_l_mm"] == pytest.approx(100.0)


def test_single_ended_connector_layout_has_one_launch_and_one_ideal_port(tmp_path: Path) -> None:
    params = stackup_params(name="single_connector_probe", line_l_mm=100.0, via_count=2)
    layout = build_single_connector_layout(params)
    layout_json = to_dict(layout)
    app = FakeApp()

    names = create_geometry(
        app,
        layout_json,
        GeometryBuildOptions(
            gnd_boundary_mode="port-edges",
            signal_layer="ETCH_TOP",
            reference_ground_layer="ETCH_INNER1",
            via_top_layer="ETCH_TOP",
            via_bottom_layer="ETCH_BOTTOM",
            ground_plane_name="hfss_ground_plane",
        ),
    )
    outputs = write_fixture_outputs(params, tmp_path, fixture_type=SINGLE_CONNECTOR_FIXTURE_TYPE)
    params_payload = json.loads(outputs["params"].read_text(encoding="utf-8"))

    assert layout.metadata["fixture_type"] == SINGLE_CONNECTOR_FIXTURE_TYPE
    assert layout.metadata["connector_side"] == "P1"
    assert layout.ports[0].width == pytest.approx(params.pin_pad_w_mm)
    assert layout.ports[1].width == pytest.approx(params.line_w_mm)
    assert layout.ports[1].x == pytest.approx(launch_len(params) + params.line_l_mm)
    assert len([shape for shape in layout_json["shapes"] if shape["kind"] == "via"]) > 4
    assert "input_feed" in names
    assert "through_line" in names
    assert "output_feed" in names
    assert any(call[0] == "rect" and call[4] == "center_line_top_ground" and call[5] == "GND" for call in app.modeler.calls)
    assert params_payload["fixture_type"] == SINGLE_CONNECTOR_FIXTURE_TYPE
    assert params_payload["derived"]["total_len_mm"] == pytest.approx(launch_len(params) + params.line_l_mm)


def test_single_connector_can_extend_cropped_reference_planes_right() -> None:
    params = stackup_params(
        name="single_connector_cropped_reference_probe",
        line_l_mm=30.0,
        l2_cutout_enabled=True,
        l2_cutout_shape="rect",
        l2_cutout_w_mm=1.6,
        l2_cutout_l_mm=3.8,
        l2_cutout_offset_x_mm=0.15,
        l3_ground_enabled=True,
        l4_ground_enabled=True,
        launch_ground_via_enabled=False,
        connector_ground_foot_via_enabled=True,
        connector_ground_foot_via_count=2,
        connector_ground_foot_via_pitch_mm=1.2,
        connector_ground_foot_via_x_offset_mm=0.8,
        reference_ground_extend_right_mm=1.5,
        l3_ground_extend_right_mm=1.5,
        l4_ground_extend_right_mm=1.5,
    )
    layout = build_single_connector_layout(params)
    layout_json = to_dict(layout)
    app = FakeApp()

    create_geometry(
        app,
        layout_json,
        GeometryBuildOptions(
            gnd_boundary_mode="port-edges",
            signal_layer="ETCH_TOP",
            reference_ground_layer="ETCH_INNER1",
            via_top_layer="ETCH_TOP",
            via_bottom_layer="ETCH_BOTTOM",
            ground_plane_name="hfss_ground_plane",
        ),
    )

    total_l = launch_len(params) + params.line_l_mm
    assert layout.metadata["reference_ground_extend_right_mm"] == pytest.approx(1.5)
    l2_planes = [
        shape
        for shape in layout_json["shapes"]
        if shape["kind"] == "reference_ground_plane" and shape.get("metadata", {}).get("target_layer") == "reference_ground_layer"
    ]
    assert any(shape["name"] == "hfss_ground_plane" for shape in l2_planes)
    assert min(float(shape["x"]) for shape in l2_planes) == pytest.approx(0.0)
    assert max(float(shape["x"]) + float(shape["w"]) for shape in l2_planes) == pytest.approx(total_l + 1.5)
    assert any(
        shape["name"] == "l3_ground_plane"
        and shape["x"] == pytest.approx(0.0)
        and shape["w"] == pytest.approx(total_l + 1.5)
        for shape in layout_json["shapes"]
    )
    assert any(
        shape["name"] == "l4_ground_plane"
        and shape["x"] == pytest.approx(0.0)
        and shape["w"] == pytest.approx(total_l + 1.5)
        for shape in layout_json["shapes"]
    )
    foot_vias = [shape for shape in layout_json["shapes"] if shape["kind"] == "via" and shape.get("metadata", {}).get("role") == "connector_ground_foot_via"]
    assert len(foot_vias) == 4
    assert sorted({round(float(shape["x"]), 6) for shape in foot_vias}) == pytest.approx([0.8, 2.0])
    y_values = sorted({round(abs(float(shape["y"])), 6) for shape in foot_vias})
    assert len(y_values) == 1
    assert y_values[0] > params.pin_pad_w_mm / 2.0 + params.launch_ground_gap_mm


def test_single_connector_params_json_preserves_single_end_fixture_type(tmp_path: Path) -> None:
    outputs = write_fixture_outputs(stackup_params(name="single_fixture_probe"), tmp_path, fixture_type=SINGLE_CONNECTOR_FIXTURE_TYPE)

    assert load_fixture_type(outputs["params"]) == SINGLE_CONNECTOR_FIXTURE_TYPE
    assert "p2_l2_cutout_rect" not in outputs["layout_json"].read_text(encoding="utf-8")


def test_microstrip_connector_drc_rejects_too_small_clearance() -> None:
    params = stackup_params(name="connector_bad_clearance", gnd_clearance_mm=0.05)
    layout = build_layout(params)
    checks = validate_connector_layout(layout, params)

    assert any(not check.ok and check.name == "params.gnd_clearance_mm" for check in checks)
    with pytest.raises(ValueError, match="gnd_clearance_mm"):
        assert_connector_layout_valid(layout, params)


def test_microstrip_connector_params_can_be_replaced_without_losing_tuple_fields() -> None:
    params = stackup_params(name="connector_replace_probe")
    updated = replace(params, via_count=1)

    assert updated.ground_layers == ("ETCH_INNER1", "ETCH_INNER2", "ETCH_BOTTOM")


def test_microstrip_connector_manifest_records_fixture_inputs_and_metadata(tmp_path: Path) -> None:
    outputs = write_outputs(stackup_params(name="connector_manifest_probe"), tmp_path)
    layout = json.loads(outputs["layout_json"].read_text(encoding="utf-8"))
    args = hfss_args(outputs["layout_json"], tmp_path / "hfss")

    payload = build_hfss_manifest_payload(args, layout, run_id="run1")

    assert payload.inputs["layout_json"] == str(outputs["layout_json"])
    assert payload.inputs["microstrip_connector_layout_json"] == str(outputs["layout_json"])
    assert payload.inputs["connector_params_json"] == str(outputs["params"])
    assert payload.flags["fixture_type"] == FIXTURE_TYPE
    assert payload.extra["fixture_type"] == FIXTURE_TYPE
    assert payload.extra["connector_route"] == "route_a_2p5d_launch_surrogate"
    assert payload.extra["line_w_mm"] == layout["metadata"]["line_w_mm"]
    assert payload.extra["line_l_mm"] == layout["metadata"]["line_l_mm"]
    assert payload.extra["reference_plane_offset_mm"] == 0.0
    assert payload.extra["port_deembed_mm"] == 0.0
    assert payload.extra["connector_region_bbox_mm"]["P1"][0] == 0.0
    assert payload.extra["connector_port_contract"]["port_type"] == "edge-gap"
    assert payload.extra["connector_port_contract"]["gnd_boundary_mode"] == "port-edges"
    assert payload.extra["connector_port_contract"]["renormalize_impedance_ohm"] == 50.0
    assert payload.extra["connector_port_contract"]["deembed_enabled"] is False


def test_microstrip_connector_dry_run_payload_includes_connector_section(tmp_path: Path) -> None:
    outputs = write_outputs(stackup_params(name="connector_dry_run_probe"), tmp_path)
    layout = json.loads(outputs["layout_json"].read_text(encoding="utf-8"))
    args = hfss_args(outputs["layout_json"], tmp_path / "hfss")
    context = SimulationRunContext(
        project_id=args.project_id,
        round_id=args.round_id,
        candidate_id="connector_dry_run_probe_jlc04161h_7628_1p6mm",
        profile_id=args.profile_id,
        simulator="hfss3dlayout",
        run_id="run1",
    )

    payload = hfss_dry_run_payload(
        args,
        layout,
        summary=collect_layout_summary(layout),
        stackup_config=load_stackup_config(args.stackup_config),
        manifest_context=context,
        run_id="run1",
        run_dir=tmp_path / "runs" / "run1",
    )

    assert payload["mode"] == "dry_run"
    assert payload["connector"]["fixture_type"] == FIXTURE_TYPE
    assert payload["connector"]["connector_params_json"] == str(outputs["params"])
    assert payload["connector"]["microstrip_connector_layout_json"] == str(outputs["layout_json"])
    assert payload["connector"]["connector_port_contract"]["reference_name"] == "GND:ETCH_INNER1:hfss_ground_plane"
    assert payload["gnd_boundary"]["metadata"]["gnd_boundary_mode"] == "port-edges"


def test_microstrip_connector_manifest_writer_records_connector_artifacts(tmp_path: Path) -> None:
    outputs = write_outputs(stackup_params(name="connector_artifact_probe"), tmp_path)
    layout = json.loads(outputs["layout_json"].read_text(encoding="utf-8"))
    run_dir = tmp_path / "runs" / "run1"
    args = hfss_args(outputs["layout_json"], tmp_path / "hfss", dry_run=False, run_dir=run_dir)

    paths = write_hfss_manifests(
        args,
        layout,
        run_id="run1",
        run_dir=run_dir,
        status="completed",
        stage="completed",
        elapsed_s=1.0,
    )

    run_manifest = json.loads(paths["run_manifest"].read_text(encoding="utf-8"))
    artifact_manifest = json.loads(paths["artifact_manifest"].read_text(encoding="utf-8"))

    assert run_manifest["extra"]["fixture_type"] == FIXTURE_TYPE
    assert run_manifest["inputs"]["connector_params_json"] == str(outputs["params"])
    assert any(item["type"] == "microstrip_connector_layout_json" and item["exists"] for item in artifact_manifest["artifacts"])
    assert any(item["type"] == "connector_params" and item["exists"] and item["hash"] for item in artifact_manifest["artifacts"])
