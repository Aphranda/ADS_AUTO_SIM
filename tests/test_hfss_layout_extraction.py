from __future__ import annotations

import importlib.util
from pathlib import Path
import pytest


_TOOL = Path(__file__).resolve().parents[1] / "tools" / "hfss" / "extract_hfss3dlayout_parameterized_layout.py"
_SPEC = importlib.util.spec_from_file_location("extract_layout", _TOOL)
assert _SPEC and _SPEC.loader
extract_layout = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(extract_layout)


def test_parse_mil_and_numeric_si_units_to_mm() -> None:
    assert extract_layout._parse_mm("12.5mil") == 0.3175
    assert extract_layout._parse_mm("590.551", default_unit="mil") == pytest.approx(14.9999954)


def test_bbox_and_distance() -> None:
    bbox = extract_layout._bbox_mm([-0.000159, 0.01484, 0.000159, 0.015159], numeric_unit="m")
    assert bbox == pytest.approx([-0.159, 14.84, 0.159, 15.159])
    assert extract_layout._distance_to_bbox([0.0, 15.0], bbox) == 0.0
    assert extract_layout._distance_to_bbox([1.0, 15.0], bbox) == pytest.approx(0.841)


def test_distill_deduplicates_vias_and_keeps_void_geometry() -> None:
    payload = {
        "project": "demo.aedt",
        "design": "RF_IN_cutout",
        "ports": ["Port1", "S1_1_Pin_T1"],
        "objects": [
            {
                "name": "signal",
                "type": "line",
                "layer": "TOP",
                "net": "N00061",
                "bbox_mm": [0.0, 0.0, 1.0, 1.0],
            },
            {
                "name": "cutout",
                "type": "poly",
                "layer": "L2_GND",
                "net": None,
                "is_void": True,
                "bbox_mm": [-1.0, -1.0, 2.0, 2.0],
            },
            {
                "name": "via_1",
                "type": "via",
                "layer": "TOP",
                "net": "GND",
                "location_mm": [1.2, 0.0],
            },
            {
                "name": "via_1",
                "type": "via",
                "layer": "L2_GND",
                "net": "GND",
                "location_mm": [1.2, 0.0],
            },
        ],
        "components": {},
        "api_limits": [],
    }
    distilled = extract_layout._distill(payload, signal_nets=["N00061"])
    assert distilled["signal_bbox_mm"] == [0.0, 0.0, 1.0, 1.0]
    assert distilled["void_bbox_mm"] == [-1.0, -1.0, 2.0, 2.0]
    assert distilled["gnd_via_count"] == 1
    assert distilled["nearby_gnd_via_candidates"][0]["distance_to_signal_bbox_mm"] == pytest.approx(0.2)
