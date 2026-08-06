from __future__ import annotations

import importlib.util
from pathlib import Path


_TOOL = Path(__file__).resolve().parents[1] / "tools" / "hfss" / "render_hfss3dlayout_api_layout_svg.py"
_SPEC = importlib.util.spec_from_file_location("render_layout_svg", _TOOL)
assert _SPEC and _SPEC.loader
render_layout_svg = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(render_layout_svg)


def _sample_payload() -> dict:
    return {
        "design": "RF_IN_cutout",
        "model_units": "mil",
        "layers_requested": ["TOP", "L2_GND", "L3_SIG"],
        "signal_nets": ["N00061"],
        "objects": [
            {
                "name": "poly__302",
                "type": "poly",
                "layer": "TOP",
                "net": "N00061",
                "bbox_mm": [-0.4, 10.9, 0.4, 14.5],
                "points_mm": [[-0.1, 10.9], [0.2, 10.9], [0.4, 14.5], [-0.4, 14.5]],
            },
            {
                "name": "poly__128",
                "type": "poly",
                "layer": "L2_GND",
                "net": None,
                "is_void": True,
                "bbox_mm": [-0.8, 13.6, 0.8, 17.6],
                "points_mm": [[-0.8, 17.6], [0.8, 17.6], [0.8, 13.6], [-0.8, 13.6]],
            },
            {
                "name": "via_570",
                "type": "via",
                "layer": "TOP",
                "net": "GND",
                "location_mm": [-1.0, 10.2],
            },
            {
                "name": "Port2",
                "type": "Pin",
                "layer": "TOP",
                "net": "N00061",
                "location_mm": [0.0, 10.8],
            },
            {
                "name": "line__136",
                "type": "line",
                "layer": "L3_SIG",
                "net": "S0_CB",
                "bbox_mm": [0.6, 3.7, 38.2, 12.7],
                "center_line_points_mm": [[0.8, 3.8], [38.1, 11.8]],
            },
            {
                "name": "line__short_ctrl",
                "type": "line",
                "layer": "L3_SIG",
                "net": "CTRL1",
                "bbox_mm": [-2.0, 9.0, 3.0, 9.2],
                "center_line_points_mm": [[-2.0, 9.1], [3.0, 9.1]],
            },
        ],
        "modeler_components": {
            "U0": {
                "name": "U0",
                "part": "Component_0",
                "placement_layer": "TOP",
                "bbox_mm": [-0.27, 9.30, 0.27, 11.18],
                "location_mm": [0.0, 10.24],
                "pins": {
                    "Port2": {
                    "net": "N00061",
                        "start_layer": "TOP",
                        "location_mm": [0.0, 10.8],
                        "bbox_mm": [0.0, 0.0, 0.0, 0.0],
                    },
                    "Port3": {
                        "net": "S0_RFC",
                        "start_layer": "TOP",
                        "location_mm": [0.0, 9.7],
                        "bbox_mm": [0.0, 0.0, 0.0, 0.0],
                    },
                },
            }
        },
    }


def test_render_svg_contains_layers_objects_and_units() -> None:
    svg = render_layout_svg.render_svg(_sample_payload(), width_px=360)
    assert svg.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "<svg" in svg
    assert "TOP layer" in svg
    assert "L1 TOP layer" in svg
    assert "L2 GND layer" in svg
    assert svg.index("L1 TOP layer") < svg.index("L2 GND layer") < svg.index("L3 SIG layer")
    assert "N00061" in svg
    assert "poly__302" in svg
    assert "poly__128" in svg
    assert "line__136" not in svg
    assert "line__short_ctrl" in svg
    assert "U0.Port2" in svg
    assert "Component_0" in svg
    assert "clip-overlay" in svg
    assert svg.index("L3 SIG layer") < svg.index("Overlay - selected")
    assert "Model units: mil -&gt; mm" in svg


def test_render_file_creates_parent_directories(tmp_path: Path) -> None:
    source = tmp_path / "in.json"
    out = tmp_path / "nested" / "layout.svg"
    source.write_text(render_layout_svg.json.dumps(_sample_payload()), encoding="utf-8")
    args = type(
        "Args",
        (),
        {
            "input": source,
            "output": out,
            "layers": None,
            "signal_nets": None,
            "full_extent": False,
            "margin_mm": 1.0,
            "crop": None,
            "width_px": 360,
            "signal_only": False,
            "max_object_span_mm": 15.0,
            "solid_gnd_layers": None,
        },
    )()
    assert render_layout_svg.render_file(args) == out
    text = out.read_text(encoding="utf-8")
    assert "RF_IN_cutout" in text


def test_solid_ground_override_keeps_other_layers_and_adds_planes() -> None:
    svg = render_layout_svg.render_svg(
        _sample_payload(),
        solid_gnd_layers=["L3_SIG"],
        width_px=360,
    )
    assert "solid_gnd_L3_SIG" in svg
    assert "Preview solid GND: L3_SIG" in svg
    assert "line__short_ctrl" not in svg
